"""表定义。学习记录拆成三张表，和前端 localStorage 里 StudyData 的几个字段对应。"""

from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))  # 只存哈希，不存密码本身
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class StudyDay(Base):
    """每天学了多少秒、完成几个番茄钟。对应前端的 days 和 pomodoros。"""

    __tablename__ = "study_days"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), primary_key=True)  # 2026-11-12
    seconds: Mapped[int] = mapped_column(default=0)
    pomodoros: Mapped[int] = mapped_column(default=0)


class SectionStat(Base):
    """每节学了多少秒、有没有勾「学完了」。对应前端的 sections 和 done。"""

    __tablename__ = "section_stats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    section_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    seconds: Mapped[int] = mapped_column(default=0)
    done: Mapped[bool] = mapped_column(default=False)


class SyncBatch(Base):
    """处理过的同步批次。同一批次重复发过来（比如网络断了前端重试）只算一次，时长不会被加两遍。"""

    __tablename__ = "sync_batches"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Guest(Base):
    """没登录的访客。前端随机生成一个 id 存在浏览器里，用它统计访客学了多久。"""

    __tablename__ = "guests"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # 第一次上报的时间
    last_seen: Mapped[datetime] = mapped_column(server_default=func.now())  # 最近一次上报的时间
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)  # 后来注册 / 登录成了哪个用户


class GuestDay(Base):
    """访客每天学了多少秒。"""

    __tablename__ = "guest_days"

    guest_id: Mapped[str] = mapped_column(ForeignKey("guests.id"), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), primary_key=True)
    seconds: Mapped[int] = mapped_column(default=0)
