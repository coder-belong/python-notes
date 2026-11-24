# app/services/files.py（3.19 新建：上传文件的检查和保存）
from __future__ import annotations

import re
import uuid
from pathlib import Path

from app.config import settings
from app.errors import fail
from app.models import User

MAX_SIZE = 5 * 1024 * 1024                    # 最大 5 MB
ALLOWED = {".png", ".jpg", ".jpeg", ".pdf", ".txt", ".md"}   # 允许的扩展名：白名单，不在里面的一律拒绝
SAVED_NAME = re.compile(r"^[0-9a-f]{32}\.[a-z]+$")          # 保存后的文件名格式：32 位随机串 + 扩展名


def user_dir(user: User) -> Path:
    """每个用户一个文件夹：uploads/1/、uploads/2/……"""
    return Path(settings.upload_dir) / str(user.id)


def save_file(user: User, filename: str, data: bytes) -> dict:
    """检查并保存一个上传的文件，返回文件信息。"""
    ext = Path(filename).suffix.lower()       # "报告.PDF" → ".pdf"
    if ext not in ALLOWED:
        raise fail(400, f"不支持的文件类型：{ext or '没有扩展名'}")
    if len(data) > MAX_SIZE:
        raise fail(413, "文件不能超过 5 MB")
    if not data:
        raise fail(400, "文件是空的")

    name = f"{uuid.uuid4().hex}{ext}"         # 存盘用随机名：不用用户给的名字，防止重名覆盖、防止 ../ 这种路径
    folder = user_dir(user)
    folder.mkdir(parents=True, exist_ok=True)   # 文件夹不存在就建，存在也不报错
    (folder / name).write_bytes(data)         # 写到磁盘
    return {"name": name, "original": filename, "size": len(data), "url": f"/files/{name}"}


def file_path(user: User, name: str) -> Path:
    """找自己的一个文件，找不到 404。"""
    if not SAVED_NAME.match(name):            # 名字格式不对（比如 ../../.env），直接当不存在
        raise fail(404, "没有这个文件")
    path = user_dir(user) / name              # 只在自己的文件夹里找：别人的文件拿不到
    if not path.is_file():
        raise fail(404, "没有这个文件")
    return path
