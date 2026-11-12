"""接口：注册、登录、查当前用户、同步学习进度。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import Session

from . import errors
from .db import Base, Db, engine
from .errors import fail, success
from .models import SectionStat, StudyDay, SyncBatch, User
from .schemas import AuthIn, SyncIn
from .security import CurrentUser, create_token, hash_password, verify_password


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
    return success(auth_result(user), "注册成功")


@app.post("/auth/login")
def login(body: AuthIn, session: Db) -> dict:
    user = session.scalar(select(User).where(User.username == body.username))
    # 用户名不存在和密码错都报同一句话，不让别人试出哪些用户名注册过
    if user is None or not verify_password(body.password, user.password_hash):
        raise fail(401, "用户名或密码不对")
    return success(auth_result(user), "登录成功")


@app.get("/auth/me")
def me(user: CurrentUser) -> dict:
    return success({"username": user.username})


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
