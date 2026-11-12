"""统一响应格式：成功 {code: 200, msg, data}，失败 {code: -1, msg, data: null}。和笔记第 3.4 节一样。"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, status: int, msg: str) -> None:
        super().__init__(msg)
        self.status = status
        self.msg = msg


def success(data: object = None, msg: str = "ok") -> dict:
    return {"code": 200, "msg": msg, "data": data}


def fail(status: int, msg: str) -> ApiError:
    return ApiError(status, msg)


def error_response(status: int, msg: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": -1, "msg": msg, "data": None})


# 参数校验失败时，把 pydantic 的英文提示换成中文；没列到的照原样返回
FIELD_NAMES = {"username": "用户名", "password": "密码"}


def validation_msg(err: dict) -> str:
    field = FIELD_NAMES.get(str(err["loc"][-1]), str(err["loc"][-1]))
    ctx = err.get("ctx") or {}
    if err["type"] == "string_too_short":
        return f"{field}至少 {ctx['min_length']} 个字符"
    if err["type"] == "string_too_long":
        return f"{field}最多 {ctx['max_length']} 个字符"
    if err["type"] == "string_pattern_mismatch":
        if field == "用户名":
            return "用户名只能用字母、数字、下划线和汉字"
        return f"{field} 格式不对"
    if err["type"] == "missing":
        return f"缺少{field}"
    return f"{field}：{err['msg']}"


def install(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        return error_response(exc.status, exc.msg)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(422, validation_msg(exc.errors()[0]))

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        msgs = {404: "没有这个接口", 405: "这个接口不支持这种请求方式"}
        return error_response(exc.status_code, msgs.get(exc.status_code, str(exc.detail)))

    @app.exception_handler(Exception)
    async def handle_unknown(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("未处理的异常")  # 完整堆栈打到日志里（Vercel 的 Logs 页能看到）
        return error_response(500, "服务出错了，请稍后再试")
