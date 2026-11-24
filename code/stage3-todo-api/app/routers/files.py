# app/routers/files.py（3.19 新建：上传、下载文件）
from __future__ import annotations

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

from app.response import success
from app.security import CurrentUser
from app.services import files as file_service

router = APIRouter(prefix="/files", tags=["文件"])


@router.post("", status_code=201)
async def upload(file: UploadFile, user: CurrentUser) -> dict:   # 参数类型写 UploadFile：从表单里取名叫 file 的文件
    data = await file.read(file_service.MAX_SIZE + 1)   # 最多读「上限 + 1」个字节：超过上限就够判断了，不用把大文件全读进内存
    info = file_service.save_file(user, file.filename or "", data)
    return success(info, msg="上传成功")


@router.get("/{name}")
def download(name: str, user: CurrentUser) -> FileResponse:
    return FileResponse(file_service.file_path(user, name))   # 把文件原样返回，Content-Type 按扩展名自动设
