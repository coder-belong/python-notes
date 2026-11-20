# tests/test_tasks.py（3.11 的五个测试；适配 3.13 之后的代码：每个请求带 headers=auth）
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import login


def test_create_and_list(client: TestClient, auth: dict) -> None:   # 参数 client：pytest 自动传入 fixture yield 出来的 c
    r = client.post("/tasks", json={"title": "写笔记"}, headers=auth)   # 发 POST /tasks，json= 就是请求体
    assert r.status_code == 201                     # HTTP 状态码：新建成功是 201
    assert r.json()["code"] == 200                  # 响应体里的 code
    assert r.json()["data"]["title"] == "写笔记"
    assert r.json()["data"]["done"] is False        # 新建的任务默认没完成

    r = client.get("/tasks", headers=auth)          # 再查列表
    assert r.status_code == 200
    assert r.json()["data"]["total"] == 1           # 一共 1 条
    assert [t["title"] for t in r.json()["data"]["items"]] == ["写笔记"]   # 取出所有标题，应该只有「写笔记」


def test_empty_title_rejected(client: TestClient, auth: dict) -> None:
    r = client.post("/tasks", json={"title": ""}, headers=auth)   # 空标题：TaskCreate 要求至少 1 个字符
    assert r.status_code == 422                     # pydantic 校验不通过，接口函数根本不会执行


def test_duplicate_title_conflict(client: TestClient, auth: dict) -> None:
    client.post("/tasks", json={"title": "写笔记"}, headers=auth)   # 先建一条
    r = client.post("/tasks", json={"title": "写笔记"}, headers=auth)   # 再建同名的
    assert r.status_code == 409
    assert r.json() == {"code": -1, "msg": "已经有一条同名的未完成任务", "data": None}   # 整个响应体都对上


def test_finish_and_filter(client: TestClient, auth: dict) -> None:
    a = client.post("/tasks", json={"title": "a"}, headers=auth).json()["data"]["id"]   # 建任务 a，记下它的 id
    client.post("/tasks", json={"title": "b"}, headers=auth)      # 再建任务 b
    assert client.patch(f"/tasks/{a}/done", headers=auth).json()["data"]["done"] is True   # 把 a 标记完成
    data = client.get("/tasks", params={"done": False}, headers=auth).json()["data"]   # params= 拼成 ?done=false
    assert [t["title"] for t in data["items"]] == ["b"]     # 只剩 b
    assert data["total"] == 1                       # 3.14：total 和列表用同一组条件，也只算没完成的


def test_delete_then_404(client: TestClient, auth: dict) -> None:
    task_id = client.post("/tasks", json={"title": "a"}, headers=auth).json()["data"]["id"]   # 先建一条，拿到 id
    r = client.delete(f"/tasks/{task_id}", headers=auth)          # 删掉它
    assert r.status_code == 200
    assert r.json()["msg"] == "删除成功"
    r = client.get(f"/tasks/{task_id}", headers=auth)             # 再查同一个 id
    assert r.status_code == 404                     # 已经没有了
    assert r.json() == {"code": -1, "msg": "没有这个任务", "data": None}


# ---- 以下为补充：3.14 的数据隔离和分页 ----

def test_tasks_require_login(client: TestClient) -> None:
    r = client.get("/tasks")                        # 不带 token
    assert r.status_code == 401
    assert r.json() == {"code": -1, "msg": "请先登录", "data": None}


def test_users_cannot_see_each_other(client: TestClient, auth: dict) -> None:
    jerry = login(client, "jerry")                  # 再注册一个用户
    task_id = client.post("/tasks", json={"title": "读书"}, headers=auth).json()["data"]["id"]   # tom 建的

    assert client.get("/tasks", headers=jerry).json()["data"]["total"] == 0   # jerry 的列表里没有
    for r in (
        client.get(f"/tasks/{task_id}", headers=jerry),
        client.patch(f"/tasks/{task_id}/done", headers=jerry),
        client.delete(f"/tasks/{task_id}", headers=jerry),
    ):
        assert r.status_code == 404                 # 别人的任务当成不存在
        assert r.json()["msg"] == "没有这个任务"

    r = client.post("/tasks", json={"title": "读书"}, headers=jerry)   # 别人的同名任务不算重名
    assert r.status_code == 201

    r = client.get(f"/tasks/{task_id}", headers=auth)   # tom 自己的还在、没被改
    assert r.status_code == 200
    assert r.json()["data"]["done"] is False


def test_pagination(client: TestClient, auth: dict) -> None:
    for title in ["写笔记", "读书", "跑步"]:
        client.post("/tasks", json={"title": title}, headers=auth)

    data = client.get("/tasks", params={"page": 1, "size": 2}, headers=auth).json()["data"]
    assert [t["title"] for t in data["items"]] == ["跑步", "读书"]   # 新的排前面
    assert (data["total"], data["page"], data["size"]) == (3, 1, 2)

    data = client.get("/tasks", params={"page": 2, "size": 2}, headers=auth).json()["data"]
    assert [t["title"] for t in data["items"]] == ["写笔记"]          # 第 2 页只剩 1 条
    assert (data["total"], data["page"], data["size"]) == (3, 2, 2)

    r = client.get("/tasks", params={"size": 500}, headers=auth)      # 超过上限 100
    assert r.status_code == 422
    assert r.json()["msg"] == "size：Input should be less than or equal to 100"

    r = client.get("/tasks", params={"page": 0}, headers=auth)        # page 从 1 开始
    assert r.status_code == 422
