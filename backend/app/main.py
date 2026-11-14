"""接口：注册、登录、查当前用户、同步学习进度、访客上报时长，以及管理员查看所有用户和访客。"""

from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case, func, select
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import Session

from . import errors
from .db import Base, Db, engine
from .errors import fail, success
from .models import Guest, GuestDay, SectionStat, StudyDay, SyncBatch, User
from .schemas import AuthIn, GuestSyncIn, SyncIn
from .security import AdminUser, CurrentUser, create_token, hash_password, is_admin, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表（已经有的表不会动）。以后要改表结构，再换成 Alembic 做迁移
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="AI 应用开发笔记 API", lifespan=lifespan)
errors.install(app)

# 前端和接口不在同一个域名（单文件 HTML 甚至是 file:// 打开的），浏览器要求接口声明允许跨域。
# 登录凭证放在 Authorization 请求头里而不是 cookie，所以允许所有来源也不会被别的网站冒用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def auth_result(user: User) -> dict:
    return {"token": create_token(user.id), "username": user.username}


def link_guest(session: Session, guest_id: str | None, user: User) -> None:
    """登录 / 注册前是访客的话，记下这个访客后来成了哪个用户（只记第一次）。"""
    guest = session.get(Guest, guest_id) if guest_id else None
    if guest is not None and guest.user_id is None:
        guest.user_id = user.id


@app.get("/")
def health() -> dict:
    return success({"service": "python-notes-api"})


@app.post("/auth/register")
def register(body: AuthIn, session: Db) -> dict:
    """注册成功直接返回 token，前端拿到就算登录了，不用再去登录页输一遍。"""
    exists = session.scalar(select(User).where(User.username == body.username))
    if exists:
        raise fail(409, "这个用户名已经有人用了")
    user = User(username=body.username, password_hash=hash_password(body.password))
    session.add(user)
    session.commit()  # 先提交拿到 user.id，token 里要用
    link_guest(session, body.guest_id, user)
    return success(auth_result(user), "注册成功")


@app.post("/auth/login")
def login(body: AuthIn, session: Db) -> dict:
    user = session.scalar(select(User).where(User.username == body.username))
    # 用户名不存在和密码错都报同一句话，不让别人试出哪些用户名注册过
    if user is None or not verify_password(body.password, user.password_hash):
        raise fail(401, "用户名或密码不对")
    link_guest(session, body.guest_id, user)
    return success(auth_result(user), "登录成功")


@app.get("/auth/me")
def me(user: CurrentUser) -> dict:
    return success({"username": user.username, "is_admin": is_admin(user)})


def upsert(session: Session, model, values: dict, add: dict, set_: dict | None = None) -> None:
    """有这一行就在原值上加，没有就插入。

    「先查再改」在两台电脑同时同步时可能互相覆盖；
    INSERT ... ON CONFLICT DO UPDATE 是数据库一条语句做完，不会丢数据。SQLite 和 Postgres 都支持这个写法。
    """
    dialect = postgresql if session.get_bind().dialect.name == "postgresql" else sqlite
    stmt = dialect.insert(model).values(**values, **add, **(set_ or {}))
    updates = {k: getattr(model, k) + stmt.excluded[k] for k in add}
    updates.update(set_ or {})
    keys = [c.name for c in model.__table__.primary_key]
    session.execute(stmt.on_conflict_do_update(index_elements=keys, set_=updates))


def totals(session: Session, user_id: int) -> dict:
    """这个用户的全部学习记录，格式和前端 localStorage 里的 StudyData 一样。"""
    days = session.scalars(select(StudyDay).where(StudyDay.user_id == user_id)).all()
    stats = session.scalars(select(SectionStat).where(SectionStat.user_id == user_id)).all()
    return {
        "days": {d.day: d.seconds for d in days if d.seconds},
        "pomodoros": {d.day: d.pomodoros for d in days if d.pomodoros},
        "sections": {s.section_id: s.seconds for s in stats if s.seconds},
        "done": {s.section_id: True for s in stats if s.done},
    }


@app.post("/sync")
def sync(body: SyncIn, user: CurrentUser, session: Db) -> dict:
    """前端把新增的记录发上来，加到账号上，再把账号的全部记录返回去。

    发的是增量（「刚才又学了 60 秒」）而不是总数：两台电脑各学各的，加起来就是总时长，不会互相覆盖。
    每批带一个 batch_id，同一批发两次只算一次。全是空的就只是来取最新数据。
    """
    has_changes = body.days or body.pomodoros or body.sections or body.done
    seen = session.get(SyncBatch, (user.id, body.batch_id))
    if has_changes and seen is None:
        session.add(SyncBatch(user_id=user.id, batch_id=body.batch_id))
        for day in body.days.keys() | body.pomodoros.keys():
            add = {"seconds": body.days.get(day, 0), "pomodoros": body.pomodoros.get(day, 0)}
            upsert(session, StudyDay, {"user_id": user.id, "day": day}, add)
        for sid in body.sections.keys() | body.done.keys():
            key = {"user_id": user.id, "section_id": sid}
            set_ = {"done": body.done[sid]} if sid in body.done else None
            upsert(session, SectionStat, key, {"seconds": body.sections.get(sid, 0)}, set_)
        session.commit()
    return success(totals(session, user.id))


@app.post("/guest/sync")
def guest_sync(body: GuestSyncIn, session: Db) -> dict:
    """没登录的访客上报学习时长，不需要 token。

    发的是每天的总秒数，不是增量：访客的记录只在一个浏览器里，发重了取较大的那个就行，不会多算。
    """
    guest = session.get(Guest, body.guest_id)
    if guest is None:
        guest = Guest(id=body.guest_id)
        session.add(guest)
    else:
        guest.last_seen = func.now()
    for day, seconds in body.days.items():
        row = session.get(GuestDay, (body.guest_id, day))
        if row is None:
            session.add(GuestDay(guest_id=body.guest_id, day=day, seconds=seconds))
        elif seconds > row.seconds:
            row.seconds = seconds
    return success()


def as_utc(t: datetime | None) -> str | None:
    """数据库 now() 存的是 UTC 时间但不带时区，补上时区再给前端，前端才能换算成本地时间。"""
    if t is None:
        return None
    return (t if t.tzinfo else t.replace(tzinfo=UTC)).isoformat()


@app.get("/admin/users")
def admin_users(
    _admin: AdminUser,
    session: Db,
    today: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
) -> dict:
    """所有用户的学习情况，按累计时长从多到少。

    日期都是前端按用户本地时间记的字符串（2026-11-13），所以「今天」也让管理员的前端传过来，
    不用服务器的日期：服务器在 UTC，北京时间早上 8 点前会差一天。
    """
    today = today or date.today().isoformat()
    week_start = (date.fromisoformat(today) - timedelta(days=6)).isoformat()  # 含今天共 7 天

    # 每个用户的学习天数据汇总成一行：一条 SQL 按 user_id 分组算完，不用把每天的记录都查出来
    days = (
        select(
            StudyDay.user_id,
            func.sum(StudyDay.seconds).label("total"),
            func.sum(case((StudyDay.day == today, StudyDay.seconds), else_=0)).label("today"),
            func.sum(case((StudyDay.day >= week_start, StudyDay.seconds), else_=0)).label("week"),
            func.count(case((StudyDay.seconds >= 60, 1))).label("days"),  # 学满 1 分钟才算学了一天
            func.max(case((StudyDay.seconds > 0, StudyDay.day))).label("last_day"),
            func.sum(StudyDay.pomodoros).label("pomodoros"),
        )
        .group_by(StudyDay.user_id)
        .subquery()
    )
    done = (
        select(SectionStat.user_id, func.count().label("done"))
        .where(SectionStat.done.is_(True))
        .group_by(SectionStat.user_id)
        .subquery()
    )
    rows = session.execute(
        select(User.username, User.created_at, days, done.c.done)
        .outerjoin(days, days.c.user_id == User.id)  # outerjoin：注册了还没学过的用户也要列出来
        .outerjoin(done, done.c.user_id == User.id)
    ).all()

    users = [
        {
            "username": r.username,
            "created_at": as_utc(r.created_at),
            "total_seconds": r.total or 0,
            "today_seconds": r.today or 0,
            "week_seconds": r.week or 0,
            "study_days": r.days or 0,
            "last_day": r.last_day,
            "pomodoros": r.pomodoros or 0,
            "done_sections": r.done or 0,
        }
        for r in rows
    ]
    users.sort(key=lambda u: u["total_seconds"], reverse=True)
    return success({"today": today, "users": users})


@app.get("/admin/guests")
def admin_guests(
    _admin: AdminUser,
    session: Db,
    today: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
) -> dict:
    """访客（没登录）的学习情况：汇总数字，加上最近来过的 200 个访客。「今天」的算法同 /admin/users。"""
    today = today or date.today().isoformat()
    days = (
        select(
            GuestDay.guest_id,
            func.sum(GuestDay.seconds).label("total"),
            func.sum(case((GuestDay.day == today, GuestDay.seconds), else_=0)).label("today"),
            func.max(case((GuestDay.seconds > 0, GuestDay.day))).label("last_day"),
        )
        .group_by(GuestDay.guest_id)
        .subquery()
    )
    rows = session.execute(
        select(Guest.id, Guest.created_at, User.username.label("became"), days)
        .outerjoin(days, days.c.guest_id == Guest.id)
        .outerjoin(User, User.id == Guest.user_id)
        .order_by(Guest.last_seen.desc())
        .limit(200)
    ).all()

    # 汇总数字按全部访客算，不受上面 200 条的限制
    summary = session.execute(
        select(
            func.count(Guest.id),
            func.count(Guest.user_id),  # count(列) 只数不是 NULL 的：后来注册 / 登录了的访客
            func.coalesce(func.sum(days.c.total), 0),
            func.count(case((days.c.today > 0, 1))),
        ).outerjoin(days, days.c.guest_id == Guest.id)
    ).one()

    guests = [
        {
            "id": r.id,
            "created_at": as_utc(r.created_at),
            "total_seconds": r.total or 0,
            "today_seconds": r.today or 0,
            "last_day": r.last_day,
            "became": r.became,
        }
        for r in rows
    ]
    return success(
        {
            "today": today,
            "total_guests": summary[0],
            "converted": summary[1],
            "total_seconds": summary[2],
            "today_guests": summary[3],
            "guests": guests,
        }
    )
