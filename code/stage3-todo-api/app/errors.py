# app/errors.py（3.5 完整版）
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError      # ② 参数校验失败时 FastAPI 抛的异常
from fastapi.responses import JSONResponse                 # 自己决定状态码和响应体
from starlette.exceptions import HTTPException as StarletteHTTPException   # ③ 404 / 405 时框架抛的异常


class ApiError(Exception):                      # 业务错误
    def __init__(self, status: int, msg: str) -> None:
        super().__init__(msg)                   # 打印这个异常时显示 msg
        self.status = status                    # HTTP 状态码：404、409……
        self.msg = msg                          # 给用户看的提示


def fail(status: int, msg: str) -> ApiError:    # 接口里 raise fail(状态码, 提示)
    return ApiError(status, msg)


def task_not_found() -> ApiError:               # 常用的错误写成函数
    return fail(404, "没有这个任务")


def error_response(status: int, msg: str) -> JSONResponse:
    """所有错误都用这一个格式返回。"""
    return JSONResponse(status_code=status, content={"code": -1, "msg": msg, "data": None})   # 下面 4 个处理器都调它


def install(app: FastAPI) -> None:
    """统一的错误拦截：不管哪种错误，前端收到的都是 {code: -1, msg, data: null}。"""

    @app.exception_handler(ApiError)             # ① 业务错误：抛出 ApiError 时调用下面这个函数
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:   # exc 就是接口里 raise 的那个对象
        return error_response(exc.status, exc.msg)   # 状态码和提示都来自 fail(...) 的两个参数

    @app.exception_handler(RequestValidationError)   # ② 参数没通过校验时，FastAPI 抛这个异常
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]           # 可能有好几条，只取第一条
        field = first["loc"][-1]          # 出错的位置，如 ["body", "title"]，取最后一个 → "title"
        return error_response(422, f"{field}：{first['msg']}")   # 返回 422 和「title：Field required」这样的提示

    @app.exception_handler(StarletteHTTPException)   # ③ 访问了不存在的路径、用错了请求方法时抛这个异常
    async def handle_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        msgs = {404: "没有这个接口", 405: "这个接口不支持这种请求方式"}   # 状态码 → 中文提示
        return error_response(exc.status_code, msgs.get(exc.status_code, str(exc.detail)))   # 其他状态码就用原来的英文说明

    @app.exception_handler(Exception)            # ④ 兜底：Exception 是所有异常的父类，什么都能接住
    async def handle_unknown(request: Request, exc: Exception) -> JSONResponse:
        # 完整的报错堆栈 uvicorn 会打印在终端里，这里不把细节给前端
        return error_response(500, "服务出错了，请稍后再试")   # 只给一句通用提示
