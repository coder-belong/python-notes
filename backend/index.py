"""Vercel 的入口：Vercel 会找这个文件里叫 app 的 FastAPI 对象。本地开发用 uvicorn app.main:app。"""

from app.main import app

__all__ = ["app"]
