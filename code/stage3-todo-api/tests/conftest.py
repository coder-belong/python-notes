# tests/conftest.py
# 拼装补充：3.11 的「准备」和「fixture」两块原样搬到这里（pytest 会自动加载 conftest.py，所有测试文件都能用 client），
# 另外加了 login 帮手和 auth fixture：3.13 之后任务接口都要登录，不带 token 会 401。
from __future__ import annotations

import os
from collections.abc import Iterator

import pytest                                       # 测试框架
from fastapi.testclient import TestClient           # 不启动服务，直接在代码里给 app 发请求
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, db_session                 # db_session：要被换掉的那个依赖（第 3.9 节）
from app.redis_client import get_redis              # 3.20：Redis 也换成测试用的库
from app.main import app                            # 要测的 app


# 测试专用的库，和开发用的 stage3_todo 库分开：测试会把它清空
# 7.6：CI 里的数据库地址不一样（带用户名密码），所以先看环境变量，没有再用本机的
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg://localhost:5432/stage3_todo_test")
engine = create_engine(TEST_DATABASE_URL)                                       # 连测试库
TestSession = sessionmaker(engine, autoflush=False, expire_on_commit=False)    # 测试库的会话工厂，参数和 db.py 里一样
test_redis = Redis.from_url(os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15"), decode_responses=True)   # 3.20：测试用 15 号库，和开发用的 0 号分开


@pytest.fixture                                     # 标记成 fixture：测试函数参数里写 client，pytest 就先跑它
def client() -> Iterator[TestClient]:
    # 每个测试开始前删表、重建：上一个测试留下的数据清干净，测试之间互不影响
    Base.metadata.drop_all(engine)                  # DROP TABLE tasks, users ...
    Base.metadata.create_all(engine)                # CREATE TABLE users, tasks ...

    def test_db_session() -> Iterator[Session]:     # 测试版的 db_session：连的是测试库
        session = TestSession()
        try:
            yield session                           # 交给接口用
            session.commit()                        # 接口正常返回后提交
        finally:
            session.close()                         # 不管怎样都关闭

    test_redis.flushdb()                            # 3.20：清空测试用的 Redis 库
    app.dependency_overrides[db_session] = test_db_session   # 把真库换成测试库；current_user 里的 Db 也会跟着换
    app.dependency_overrides[get_redis] = lambda: test_redis   # 3.20：Redis 也换成测试库
    with TestClient(app) as c:                      # with：启动、关闭 app
        yield c                                     # 把 client 交给测试函数，测试跑完再回到这里
    app.dependency_overrides.clear()                # 收尾：撤掉替换，不影响别的地方


def login(client: TestClient, username: str = "tom", password: str = "123456") -> dict:
    """注册一个用户，返回带 token 的请求头：{"Authorization": "Bearer eyJ..."}。"""
    r = client.post("/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201
    return {"Authorization": f"Bearer {r.json()['data']['token']}"}


@pytest.fixture
def auth(client: TestClient) -> dict:
    """已登录用户 tom 的请求头，测试里写 headers=auth。"""
    return login(client)
