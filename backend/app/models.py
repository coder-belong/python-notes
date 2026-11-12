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
