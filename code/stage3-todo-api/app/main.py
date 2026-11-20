# app/main.py（3.16 完整版：3.15 去掉 lifespan / create_all，3.16 加 CORS、日志中间件、健康检查）
from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app import errors
from app.config import settings
from app.response import success              # 拼装补充：笔记 health() 写的是 errors.success，errors 里没有 success，改用 response.success
from app.routers import auth, tasks

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")   # 日志格式
logger = logging.getLogger("todo-api")

app = FastAPI(title="todo-api")         # 不再 create_all：表结构交给 alembic
errors.install(app)                     # 登记错误处理器

app.add_middleware(                     # 跨域：允许这些网址的前端页面调接口
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # 从配置里读允许的网址
    allow_methods=["*"],                 # 所有请求方法
    allow_headers=["*"],                 # 所有请求头，包括 Authorization
)


@app.middleware("http")                          # 每个请求进来、出去都会经过这里
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start = time.perf_counter()                  # 接口执行前
    response = await call_next(request)          # 交给后面的路由去处理，拿到响应
    ms = (time.perf_counter() - start) * 1000    # 接口执行后：用了多少毫秒
    logger.info("%s %s → %s %.0fms", request.method, request.url.path, response.status_code, ms)
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"   # 也可以改响应：加个响应头
    return response


app.include_router(auth.router)          # /auth/...
app.include_router(tasks.router)         # /tasks/...


@app.get("/", tags=["健康检查"])         # GET /，/docs 里单独一组
def health() -> dict:
    """部署后先访问这个，确认服务起来了。"""
    return success({"status": "ok"})     # {"code": 200, "msg": "ok", "data": {"status": "ok"}}
