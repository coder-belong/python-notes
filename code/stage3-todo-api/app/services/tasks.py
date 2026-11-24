# app/services/tasks.py（3.17 新建：任务的业务逻辑。只管「能不能做、怎么做」，不管 HTTP）
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import fail, task_not_found
from app.models import Task, User
from app.schemas import TaskCreate


def get_task(session: Session, user: User, task_id: int) -> Task:
    """取自己的一条任务。别人的任务也当成不存在：抛 404。"""
    task = session.get(Task, task_id)                    # SELECT * FROM tasks WHERE id = ...
    if task is None or task.user_id != user.id:          # 不存在，或者不是自己的
        raise task_not_found()
    return task


def list_tasks(session: Session, user: User, done: bool | None, page: int, size: int) -> tuple[list[Task], int]:
    """查自己的任务，返回（这一页的任务，符合条件的总数）。"""
    conditions = [Task.user_id == user.id]               # WHERE user_id = 1
    if done is not None:
        conditions.append(Task.done == done)             # AND done = ...
    total = session.scalar(select(func.count()).select_from(Task).where(*conditions)) or 0   # SELECT count(*) ...
    stmt = select(Task).where(*conditions).order_by(Task.id.desc()).offset((page - 1) * size).limit(size)
    return list(session.scalars(stmt)), total


def create_task(session: Session, user: User, data: TaskCreate) -> Task:
    """新建任务：同一个人不能有两条同名的未完成任务。"""
    same = select(Task).where(Task.user_id == user.id, Task.title == data.title, Task.done.is_(False))
    if session.scalar(same):                             # 查到一条就算重名
        raise fail(409, "已经有一条同名的未完成任务")
    task = Task(user_id=user.id, title=data.title, note=data.note)
    session.add(task)
    session.commit()                                     # INSERT INTO tasks ...
    return task


def finish_task(session: Session, user: User, task_id: int) -> Task:
    task = get_task(session, user, task_id)              # 先确认是自己的
    task.done = True
    session.commit()                                     # UPDATE tasks SET done = true ...
    return task


def delete_task(session: Session, user: User, task_id: int) -> None:
    session.delete(get_task(session, user, task_id))     # 先确认是自己的，再记下「要删除」
    session.commit()                                     # DELETE FROM tasks WHERE id = ...
