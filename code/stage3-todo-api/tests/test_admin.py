# tests/test_admin.py（3.18：角色权限）
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import update

from app.models import User
from tests.conftest import TestSession, login


def make_admin(username: str) -> None:
    """测试里直接改库，把某个用户设成管理员（真实项目里也是这样：由人在数据库里设，不开放接口）。"""
    with TestSession() as session:
        session.execute(update(User).where(User.username == username).values(role="admin"))
        session.commit()


def test_admin_only(client: TestClient, auth: dict) -> None:
    r = client.get("/admin/users")                   # 没登录
    assert r.status_code == 401

    r = client.get("/admin/users", headers=auth)     # tom 登录了，但是普通用户
    assert r.status_code == 403
    assert r.json() == {"code": -1, "msg": "没有权限", "data": None}

    make_admin("tom")                                # 把 tom 设成管理员，token 不用换
    client.post("/tasks", json={"title": "写笔记"}, headers=auth)
    login(client, "jerry")                           # 再来一个普通用户，没有任务
    r = client.get("/admin/users", headers=auth)
    assert r.status_code == 200
    assert r.json()["data"] == [
        {"id": 1, "username": "tom", "role": "admin", "total": 1, "done": 0},
        {"id": 2, "username": "jerry", "role": "user", "total": 0, "done": 0},
    ]


def test_me_has_role(client: TestClient, auth: dict) -> None:
    assert client.get("/auth/me", headers=auth).json()["data"]["role"] == "user"   # 新注册的默认是普通用户
