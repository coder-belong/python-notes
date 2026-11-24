# app/routers/tasks.py（3.12 新建；3.14 加登录和分页；3.17 业务逻辑搬到 services/tasks.py，这里只管 HTTP）
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.db import Db
from app.response import success
from app.schemas import TaskCreate, TaskList, TaskOut
from app.security import CurrentUser
from app.services import tasks as task_service   # 业务逻辑都在这里；起个别名，免得和下面的接口函数重名

router = APIRouter(prefix="/tasks", tags=["任务"])


@router.get("")
def list_tasks(
    user: CurrentUser,
    session: Db,
    done: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict:
    items, total = task_service.list_tasks(session, user, done, page, size)   # 查数据交给 service
    return success(TaskList(items=[TaskOut.model_validate(t) for t in items], total=total, page=page, size=size))


@router.post("", status_code=201)
def create_task(body: TaskCreate, user: CurrentUser, session: Db) -> dict:
    task = task_service.create_task(session, user, body)   # 重名检查、插入都在 service 里
    return success(TaskOut.model_validate(task), msg="创建成功")


@router.get("/{task_id}")
def get_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    return success(TaskOut.model_validate(task_service.get_task(session, user, task_id)))


@router.patch("/{task_id}/done")
def finish_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    return success(TaskOut.model_validate(task_service.finish_task(session, user, task_id)))


@router.delete("/{task_id}")
def delete_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    task_service.delete_task(session, user, task_id)
    return success(msg="删除成功")
