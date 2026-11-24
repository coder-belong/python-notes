# app/security.py（3.13；3.18 末尾加 require_role / AdminUser）
from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt                                     # pyjwt：生成、校验 token
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer   # 从请求头取 Bearer token
from pwdlib import PasswordHash                # 密码哈希

from app.config import settings
from app.db import Db
from app.errors import fail
from app.models import User

password_hash = PasswordHash.recommended()     # 用 Argon2 算法


def hash_password(password: str) -> str:       # 注册时用：明文 → 哈希，存进数据库
    return password_hash.hash(password)        # 每次结果都不一样：里面带了随机的盐


def verify_password(password: str, hashed: str) -> bool:   # 登录时用：输入的密码和存的哈希对不对得上
    return password_hash.verify(password, hashed)


def create_token(user_id: int) -> str:
    payload = {                                # token 里放的内容（谁都能解开看，只放 id）
        "sub": str(user_id),                                            # 这个 token 属于谁
        "exp": datetime.now(UTC) + timedelta(days=settings.token_days),  # 过期时间，过期后 decode 会报错
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")   # 用密钥签名，得到 eyJ... 这样的字符串


bearer = HTTPBearer(auto_error=False)          # auto_error=False：没带 token 时不让 FastAPI 自己报 403，交给下面统一返回 401


def current_user(
    session: Db,                               # 依赖里还能再用依赖：拿数据库会话
    cred: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],   # 请求头里的 token，没带就是 None
) -> User:
    """依赖：从请求头 Authorization: Bearer <token> 解析出当前用户，不对就 401。"""
    if cred is None:                           # 没带 token
        raise fail(401, "请先登录")
    try:
        payload = jwt.decode(cred.credentials, settings.jwt_secret, algorithms=["HS256"])   # 验签名、验过期，通过才拿到内容
    except jwt.ExpiredSignatureError:          # 过期了
        raise fail(401, "登录已过期，请重新登录") from None
    except jwt.InvalidTokenError:              # 被改过、格式不对
        raise fail(401, "登录无效，请重新登录") from None
    user = session.get(User, int(payload["sub"]))   # SELECT * FROM users WHERE id = ...
    if user is None:                                   # token 是对的，但用户已经被删了
        raise fail(401, "账号不存在，请重新登录")
    return user                                # 接口里的 user 参数拿到的就是它


CurrentUser = Annotated[User, Depends(current_user)]   # 接口里写 user: CurrentUser 就要求登录


# ---- 3.18：按角色限制 ----

def require_role(*roles: str) -> Callable[[User], User]:
    """生成一个依赖：先要求登录（CurrentUser），再要求角色在 roles 里，不在就 403。"""

    def checker(user: CurrentUser) -> User:    # 依赖里再用依赖：先跑 current_user，没登录直接 401
        if user.role not in roles:             # 登录了，但角色不够
            raise fail(403, "没有权限")
        return user

    return checker


AdminUser = Annotated[User, Depends(require_role("admin"))]   # 接口里写 _admin: AdminUser 就只有管理员能进
