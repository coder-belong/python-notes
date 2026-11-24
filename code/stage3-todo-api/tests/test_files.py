# tests/test_files.py（3.19：文件上传）
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from tests.conftest import login


@pytest.fixture(autouse=True)                        # autouse：这个文件里的每个测试都自动用上
def tmp_upload_dir(tmp_path, monkeypatch) -> None:   # tmp_path：pytest 给的临时文件夹，测完自动清理
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))   # 测试时文件存到临时文件夹，不弄脏项目


def test_upload_and_download(client: TestClient, auth: dict) -> None:
    r = client.post("/files", files={"file": ("笔记.md", "# hello".encode(), "text/markdown")}, headers=auth)
    assert r.status_code == 201
    info = r.json()["data"]
    assert info["original"] == "笔记.md" and info["size"] == 7 and info["name"].endswith(".md")

    r = client.get(info["url"], headers=auth)        # 下载回来，内容一样
    assert r.status_code == 200
    assert r.content == b"# hello"

    jerry = login(client, "jerry")
    assert client.get(info["url"], headers=jerry).status_code == 404   # 别人拿不到


def test_upload_rejected(client: TestClient, auth: dict) -> None:
    r = client.post("/files", files={"file": ("run.exe", b"MZ", "application/octet-stream")}, headers=auth)
    assert r.status_code == 400
    assert r.json()["msg"] == "不支持的文件类型：.exe"

    big = b"0" * (5 * 1024 * 1024 + 1)               # 比 5 MB 多 1 个字节
    r = client.post("/files", files={"file": ("big.txt", big, "text/plain")}, headers=auth)
    assert r.status_code == 413

    assert client.get("/files/..%2F..%2F.env", headers=auth).status_code == 404   # 想用 ../ 读别的文件
