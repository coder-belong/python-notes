# app/routers/admin.py（3.18 新建：只有管理员能用的接口；3.20 结果缓存 60 秒）
from __future__ import annotations

from fastapi import APIRouter

from app.db import Db
from app.response import success
from app.redis_client import RedisDep
from app.security import AdminUser
from app.services.cache import cached
from app.services import users as user_service

router = APIRouter(prefix="/admin", tags=["管理员"])


@router.get("/users")
def list_users(_admin: AdminUser, session: Db, r: RedisDep) -> dict:   # _admin：只用来检查权限，函数里用不到，名字前加 _
    users = cached(r, "admin:users", 60, lambda: user_service.list_users_with_counts(session))   # 60 秒内重复请求不查数据库
    return success(users)
