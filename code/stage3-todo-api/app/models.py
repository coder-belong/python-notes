# app/models.py（3.7 新建 Task；3.13 加 User；3.14 加 user_id 和 relationship；3.15 加 priority；3.18 User 加 role）
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)   # unique：不能重名
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)          # 只存哈希，不存密码
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", server_default="user")   # 3.18：角色，user 普通用户 / admin 管理员
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    tasks: Mapped[list[Task]] = relationship(back_populates="user", cascade="all, delete-orphan")   # 用户 → 他的所有任务（不是表里的列）


class Task(Base):
    __tablename__ = "tasks"                       # 数据库里的表名

    id: Mapped[int] = mapped_column(Integer, primary_key=True)          # 主键，自增
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)   # 外键：属于哪个用户；加索引，按用户查更快
    title: Mapped[str] = mapped_column(String(200), nullable=False)     # 必填
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    note: Mapped[str | None] = mapped_column(String(500))               # | None = 可以为空
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")   # 3.15：已有数据的表加非空列，一定要给 server_default
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now,   # 新建时填，修改时自动刷新
    )
    user: Mapped[User] = relationship(back_populates="tasks")          # 反过来：任务 → 用户
