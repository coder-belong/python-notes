# tests/test_app.py（补充：3.16 健康检查、CORS 预检、日志中间件；3.5 统一错误格式）
from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"code": 200, "msg": "ok", "data": {"status": "ok"}}
    assert r.headers["X-Response-Time"].endswith("ms")   # 日志中间件加的响应头


def test_cors_preflight_allowed(client: TestClient) -> None:
    r = client.options("/tasks", headers={
        "Origin": "http://localhost:5173",                # 配置里允许的前端网址
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "authorization" in r.headers["access-control-allow-headers"].lower()
    assert "X-Response-Time" in r.headers             # 日志中间件在 CORS 外层，预检也经过它


def test_cors_preflight_other_origin(client: TestClient) -> None:
    r = client.options("/tasks", headers={
        "Origin": "https://evil.example.com",             # 不在 cors_origins 里
        "Access-Control-Request-Method": "GET",
    })
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers


def test_unknown_path_and_method(client: TestClient) -> None:
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json() == {"code": -1, "msg": "没有这个接口", "data": None}
    r = client.put("/tasks/1")
    assert r.status_code == 405
    assert r.json() == {"code": -1, "msg": "这个接口不支持这种请求方式", "data": None}
