"""AI 翻译：把笔记正文一批一批翻成英文 / 日文。

- 前端把一节正文拆成一个个段落（带行内 HTML），按字数分成小批，每批调一次这个接口，翻好一批显示一批
- 每批按「语言 + 原文哈希」缓存在 translations 表里：命中缓存不用登录、不花钱，秒回
- 没缓存才调模型，要登录（防止被拿去白嫖翻译），一批控制在几千字，几秒就能翻完
"""

import hashlib
import json
import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Header
from openai import APIError
from pydantic import BaseModel, Field
from sqlalchemy import select

from .ai import client
from .config import AI_MODEL
from .db import Db
from .errors import fail, success
from .models import Translation
from .security import current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai")

LANG_NAMES = {"en": "英文（English）", "ja": "日文（日本語）"}
MAX_CHARS = 6000  # 一批最多多少字：前端按 3000 字左右分批，这里留点余量

PROMPT = """把用户发来的 JSON 里 items 数组的每一项，从中文翻译成{lang}。这是一份 Python / AI 应用开发学习笔记。
规则：
- 每一项可能带 HTML 标签：标签和属性原样保留（包括 href、class），只翻译标签之间的文字
- <code>…</code> 里的内容不翻译；代码、命令、文件名、函数名、变量名、URL 都保持原样
- 技术术语用这门语言里通行的叫法；原文里已经是英文的词保持原样
- 意思准确、读起来自然，不要逐字硬翻；不要增删内容
- 只返回 JSON：{{"items": [...]}}，数组长度、顺序和输入完全一致，一项对一项"""


class TranslateIn(BaseModel):
    lang: Literal["en", "ja"]
    items: Annotated[list[Annotated[str, Field(max_length=MAX_CHARS)]], Field(min_length=1, max_length=200)]


def src_hash(lang: str, items: list[str]) -> str:
    return hashlib.sha256(json.dumps([lang, items], ensure_ascii=False).encode()).hexdigest()


async def call_model(lang: str, items: list[str]) -> list[str] | None:
    """调一次模型翻这一批；返回的条数对不上就算失败（返回 None）。"""
    resp = await client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": PROMPT.format(lang=LANG_NAMES[lang])},
            {"role": "user", "content": json.dumps({"items": items}, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},  # 让模型一定返回合法 JSON（第 4.4 节）
        max_tokens=8000,
        temperature=0.3,
        extra_body={"thinking": {"type": "disabled"}},
    )
    try:
        out = json.loads(resp.choices[0].message.content or "")["items"]
    except (ValueError, KeyError, TypeError):
        return None
    if not isinstance(out, list) or len(out) != len(items) or not all(isinstance(x, str) for x in out):
        return None
    return out


@router.post("/translate")
async def translate(body: TranslateIn, session: Db, authorization: Annotated[str | None, Header()] = None):
    if sum(len(x) for x in body.items) > MAX_CHARS:
        raise fail(422, f"一批最多 {MAX_CHARS} 字")
    h = src_hash(body.lang, body.items)
    cached = session.scalar(select(Translation).where(Translation.lang == body.lang, Translation.src_hash == h))
    if cached is not None:
        return success({"items": cached.items, "cached": True})

    current_user(session, authorization)  # 没缓存要调模型：先确认登录了（没登录 401）
    if client is None:
        raise fail(503, "后端没有配置 DEEPSEEK_API_KEY")
    try:
        out = await call_model(body.lang, body.items)
        if out is None:  # 偶尔条数对不上：再试一次
            out = await call_model(body.lang, body.items)
    except APIError as e:
        logger.warning("翻译调用失败：%s", e)
        raise fail(502, f"翻译失败：{e.message}") from None
    if out is None:
        raise fail(502, "翻译结果格式不对，请稍后再试")

    session.add(Translation(lang=body.lang, src_hash=h, items=out))
    session.commit()
    return success({"items": out, "cached": False})
