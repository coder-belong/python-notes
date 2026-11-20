# app/routers/tasks.py（3.12 新建；3.14 整个换成这样：只操作自己的任务 + 分页）
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query           # Query：给查询参数加校验（分页用）
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import Db
from app.errors import fail, task_not_found
from app.models import Task, User
from app.response import success
from app.schemas import TaskCreate, TaskList, TaskOut
from app.security import CurrentUser           # 要求登录（第 3.13 节）

router = APIRouter(prefix="/tasks", tags=["任务"])


def load_task(session: Session, task_id: int, user: User) -> Task:
    """取自己的一条任务。别人的任务也当成不存在：返回 404，不告诉对方「有这条，但不是你的」。"""
    task = session.get(Task, task_id)          # SELECT * FROM tasks WHERE id = ...
    if task is None or task.user_id != user.id:   # 不存在，或者不是自己的
        raise task_not_found()                 # 都返回 404
    return task


@router.get("")
def list_tasks(
    user: CurrentUser,                                   # 当前登录的用户，没登录就 401
    session: Db,
    done: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,              # 第几页，从 1 开始
    size: Annotated[int, Query(ge=1, le=100)] = 20,     # 每页几条，最多 100，防止一次拉太多
) -> dict:
    conditions = [Task.user_id == user.id]               # 只查自己的：WHERE user_id = 1
    if done is not None:
        conditions.append(Task.done == done)             # 再加 AND done = ...

    total = session.scalar(select(func.count()).select_from(Task).where(*conditions))   # SELECT count(*) FROM tasks WHERE user_id = 1 AND done = false：和下面列表同一组条件
    # 拼成一条 SQL（以 page=2、size=20、done=false 为例）：
    # SELECT * FROM tasks WHERE user_id = 1 AND done = false ORDER BY id DESC LIMIT 20 OFFSET 20
    stmt = (
        select(Task)                                     # SELECT * FROM tasks
        .where(*conditions)                              # WHERE user_id = 1 AND done = false：和上面 count 用同一组条件
        .order_by(Task.id.desc())                        # ORDER BY id DESC：新的排前面
        .offset((page - 1) * size)                       # OFFSET 20：跳过前面几页，(2 - 1) × 20 = 20 条
        .limit(size)                                     # LIMIT 20：这一页取几条
    )
    items = [TaskOut.model_validate(t) for t in session.scalars(stmt)]   # 这时才执行上面拼好的 SELECT，每条转成 TaskOut
    return success(TaskList(items=items, total=total or 0, page=page, size=size))


@router.post("", status_code=201)
def create_task(body: TaskCreate, user: CurrentUser, session: Db) -> dict:
    same = select(Task).where(Task.user_id == user.id, Task.title == body.title, Task.done.is_(False))   # SELECT * FROM tasks WHERE user_id = 1 AND title = '写笔记' AND done IS false：自己的、同名、未完成（只是拼好）
    if session.scalar(same):                         # 执行上面的 SELECT，查到一条就算重名
        raise fail(409, "已经有一条同名的未完成任务")
    task = Task(user_id=user.id, title=body.title, note=body.note)   # 新任务属于当前用户
    session.add(task)                                # 记下「要插入」
    session.commit()                                     # INSERT INTO tasks (user_id, title, note, ...) VALUES (1, '写周报', ...)
    return success(TaskOut.model_validate(task), msg="创建成功")


@router.get("/{task_id}")
def get_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    return success(TaskOut.model_validate(load_task(session, task_id, user)))   # 别人的任务也是 404


@router.patch("/{task_id}/done")
def finish_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    task = load_task(session, task_id, user)            # 先确认是自己的
    task.done = True
    session.commit()                                     # UPDATE tasks SET done = true, updated_at = ... WHERE id = 2
    return success(TaskOut.model_validate(task))


@router.delete("/{task_id}")
def delete_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    session.delete(load_task(session, task_id, user))   # 先确认是自己的（load_task 里 SELECT），再记下「要删除」
    session.commit()                                     # DELETE FROM tasks WHERE id = 3
    return success(msg="删除成功")
