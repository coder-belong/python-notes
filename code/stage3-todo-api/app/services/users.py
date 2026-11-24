# app/services/users.py（3.18 新建：用户相关的业务逻辑）
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Task, User


def list_users_with_counts(session: Session) -> list[dict]:
    """所有用户，以及每人有几条任务、完成了几条。"""
    stmt = (
        select(
            User.id,
            User.username,
            User.role,
            func.count(Task.id).label("total"),                              # 一共几条任务
            func.count(Task.id).filter(Task.done.is_(True)).label("done"),   # 其中完成了几条
        )
        .outerjoin(Task, Task.user_id == User.id)    # LEFT JOIN：没有任务的用户也要列出来
        .group_by(User.id)                           # 按用户分组统计
        .order_by(User.id)
    )
    # SELECT users.id, users.username, users.role, count(tasks.id), count(tasks.id) FILTER (WHERE tasks.done IS true)
    # FROM users LEFT JOIN tasks ON tasks.user_id = users.id GROUP BY users.id ORDER BY users.id
    return [row._asdict() for row in session.execute(stmt)]   # 每行转成字典
