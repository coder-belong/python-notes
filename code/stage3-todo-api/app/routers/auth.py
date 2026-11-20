# app/routers/auth.py（3.13）
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.db import Db
from app.errors import fail
from app.models import User
from app.response import success
from app.schemas import AuthIn, TokenOut
from app.security import CurrentUser, create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["账号"])   # 路径都以 /auth 开头，/docs 里归到「账号」


@router.post("/register", status_code=201)
def register(body: AuthIn, session: Db) -> dict:
    if session.scalar(select(User).where(User.username == body.username)):   # SELECT ... WHERE username = 'tom'，已经有了
        raise fail(409, "这个用户名已经被注册了")
    user = User(username=body.username, password_hash=hash_password(body.password))   # 存哈希，不存明文
    session.add(user)                                # 记下「要插入」
    session.commit()                           # INSERT INTO users ...，之后 user.id 有值
    return success(TokenOut(token=create_token(user.id), username=user.username), msg="注册成功")   # 直接发 token，等于已经登录


@router.post("/login")
def login(body: AuthIn, session: Db) -> dict:
    user = session.scalar(select(User).where(User.username == body.username))   # SELECT * FROM users WHERE username = 'tom'，查不到是 None
    if user is None or not verify_password(body.password, user.password_hash):   # 用户不存在、密码错，都走这里
        raise fail(401, "用户名或密码错误")      # 两种情况同一句话：不告诉别人「这个用户名是存在的」
    return success(TokenOut(token=create_token(user.id), username=user.username), msg="登录成功")


@router.get("/me")
def me(user: CurrentUser) -> dict:           # 声明要 CurrentUser：没登录进不来
    return success({"id": user.id, "username": user.username})
