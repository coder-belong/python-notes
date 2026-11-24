# tests/test_redis.py（3.20：登录失败限制、缓存）
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import login, test_redis
from tests.test_admin import make_admin


def test_login_locked_after_5_fails(client: TestClient) -> None:
    login(client, "tom", "123456")                   # 先注册 tom
    wrong = {"username": "tom", "password": "wrong-password"}
    for _ in range(5):                               # 连错 5 次
        assert client.post("/auth/login", json=wrong).status_code == 401

    r = client.post("/auth/login", json={"username": "tom", "password": "123456"})   # 第 6 次：密码对了也不行
    assert r.status_code == 429
    assert r.json()["msg"] == "密码错误次数太多，请 10 分钟后再试"

    test_redis.delete("login_fail:tom")              # 模拟 10 分钟过去：计数器过期
    r = client.post("/auth/login", json={"username": "tom", "password": "123456"})
    assert r.status_code == 200


def test_success_resets_counter(client: TestClient) -> None:
    login(client, "tom", "123456")
    client.post("/auth/login", json={"username": "tom", "password": "wrong-password"})
    assert test_redis.get("login_fail:tom") == "1"   # 错了一次
    client.post("/auth/login", json={"username": "tom", "password": "123456"})
    assert test_redis.get("login_fail:tom") is None  # 登录成功，清零


def test_admin_users_cached(client: TestClient, auth: dict) -> None:
    make_admin("tom")
    first = client.get("/admin/users", headers=auth).json()["data"]
    assert test_redis.ttl("admin:users") > 0         # 结果进了缓存，还有过期时间

    login(client, "jerry")                           # 新注册一个用户
    again = client.get("/admin/users", headers=auth).json()["data"]
    assert again == first                            # 60 秒内拿的是缓存：看不到 jerry

    test_redis.delete("admin:users")                 # 删掉缓存
    assert len(client.get("/admin/users", headers=auth).json()["data"]) == 2   # 重新查库，jerry 出来了
