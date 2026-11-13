"""密码哈希、登录 token，以及「当前登录用户」这个依赖。"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, Header
from pwdlib import PasswordHash

from .config import ADMIN_USERNAMES, JWT_SECRET, TOKEN_DAYS
from .db import Db
from .errors import fail
from .models import User

# 密码用 Argon2 算哈希后再存。哈希是单向的：能验证密码对不对，但从哈希算不回密码，数据库泄露了也拿不到原密码
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(user_id: int) -> str:
    """登录 token 用 JWT：内容是「谁、什么时候过期」，用 JWT_SECRET 签名。

    服务器不用存 token：收到时验一下签名，就知道是自己发的、没被改过。
    """
    payload = {"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(days=TOKEN_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def current_user(session: Db, authorization: Annotated[str | None, Header()] = None) -> User:
    """从请求头 Authorization: Bearer <token> 里认出是谁。没带、过期、被篡改都返回 401。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise fail(401, "请先登录")
    try:
        payload = jwt.decode(authorization.removeprefix("Bearer "), JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise fail(401, "登录已过期，请重新登录") from None
    except jwt.InvalidTokenError:
        raise fail(401, "登录信息无效，请重新登录") from None
    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise fail(401, "账号不存在，请重新登录")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def is_admin(user: User) -> bool:
    return user.username in ADMIN_USERNAMES


def admin_user(user: CurrentUser) -> User:
    """在 current_user 的基础上再检查一下是不是管理员：没登录 401，登录了但不是管理员 403。"""
    if not is_admin(user):
        raise fail(403, "只有管理员能查看")
    return user


AdminUser = Annotated[User, Depends(admin_user)]
