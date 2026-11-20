# tests/test_auth.py（补充：3.13 注册登录）
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.config import settings
from tests.conftest import login


def test_register_returns_token(client: TestClient) -> None:
    r = client.post("/auth/register", json={"username": "tom", "password": "123456"})
    assert r.status_code == 201
    assert r.json()["msg"] == "注册成功"
    assert r.json()["data"]["username"] == "tom"
    assert r.json()["data"]["token"].startswith("eyJ")   # JWT 的头部 base64 后固定是 eyJ 开头


def test_register_duplicate(client: TestClient) -> None:
    login(client, "tom")
    r = client.post("/auth/register", json={"username": "tom", "password": "abcdef"})
    assert r.status_code == 409
    assert r.json() == {"code": -1, "msg": "这个用户名已经被注册了", "data": None}


def test_register_validation(client: TestClient) -> None:
    r = client.post("/auth/register", json={"username": "tom", "password": "123"})   # 密码不到 6 位
    assert r.status_code == 422
    assert r.json()["msg"].startswith("password：")
    r = client.post("/auth/register", json={"username": "a b", "password": "123456"})   # 用户名有空格，不符合 ^\w+$
    assert r.status_code == 422
    assert r.json()["msg"].startswith("username：")


def test_login_and_me(client: TestClient) -> None:
    login(client, "tom", "123456")
    r = client.post("/auth/login", json={"username": "tom", "password": "123456"})
    assert r.status_code == 200
    assert r.json()["msg"] == "登录成功"
    token = r.json()["data"]["token"]

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["data"]["username"] == "tom"


def test_login_wrong_password_or_user(client: TestClient) -> None:
    login(client, "tom", "123456")
    wrong_pwd = client.post("/auth/login", json={"username": "tom", "password": "654321"})
    no_user = client.post("/auth/login", json={"username": "nobody", "password": "123456"})
    for r in (wrong_pwd, no_user):                  # 两种情况同一句话
        assert r.status_code == 401
        assert r.json() == {"code": -1, "msg": "用户名或密码错误", "data": None}


def test_me_token_errors(client: TestClient) -> None:
    assert client.get("/auth/me").json()["msg"] == "请先登录"

    r = client.get("/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})   # 格式不对 / 被改过
    assert r.status_code == 401
    assert r.json()["msg"] == "登录无效，请重新登录"

    expired = jwt.encode(                           # 用同一个密钥签一个已经过期的 token
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(seconds=1)}, settings.jwt_secret, algorithm="HS256",
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401
    assert r.json()["msg"] == "登录已过期，请重新登录"

    ghost = jwt.encode(                             # 签名对，但用户不存在
        {"sub": "999", "exp": datetime.now(UTC) + timedelta(days=1)}, settings.jwt_secret, algorithm="HS256",
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {ghost}"})
    assert r.status_code == 401
    assert r.json()["msg"] == "账号不存在，请重新登录"
