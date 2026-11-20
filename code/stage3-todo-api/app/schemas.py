# app/schemas.py（3.3 新建；3.10 加 TaskList；3.13 加 AuthIn / TokenOut；3.14 TaskList 加 page / size；3.15 TaskOut 加 priority）
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """新建任务的请求体。"""
    title: str = Field(min_length=1, max_length=200)   # Field 加校验规则
    note: str | None = None                            # 可以不传


class TaskOut(BaseModel):
    """返回给前端的一条任务。"""
    model_config = ConfigDict(from_attributes=True)   # 允许直接从对象创建，见 3.3 节末尾的补充

    id: int
    title: str
    done: bool
    note: str | None          # 没有默认值：必须给，但可以是 None
    priority: int             # 3.15：「要在接口里返回，TaskOut 也加上 priority: int」
    created_at: datetime      # 输出 JSON 时自动转成 ISO 字符串
    updated_at: datetime


class TaskList(BaseModel):
    items: list[TaskOut]      # 模型可以嵌套
    total: int                # 符合条件的一共多少条（不是这一页的条数）
    page: int                 # 当前第几页
    size: int                 # 每页几条


class AuthIn(BaseModel):
    """注册、登录的请求体。"""
    username: str = Field(min_length=2, max_length=20, pattern=r"^\w+$")   # 2～20 个字；\w 是字母、数字、下划线、汉字
    password: str = Field(min_length=6, max_length=128)                    # 至少 6 位


class TokenOut(BaseModel):                     # 注册、登录成功后返回的 data
    token: str                                 # 前端存起来，之后每次请求带上
    username: str                              # 页面上显示用
