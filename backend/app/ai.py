"""问 AI：在笔记里选中一段文字，结合这一节的内容提问，回答用 SSE 一段一段推给前端。
登录、并且累计学习满 10 分钟才能用（管理员不限），防止注册个账号就拿来当免费的 AI 用。

和笔记第 4.6 节的 chat_api.py 是同一个写法：
- system 里放「助教规则 + 这一节的正文」，每次请求都一样，能命中 DeepSeek 的缓存（第 4.3 节）
- 多轮对话的历史由前端保存，每次整段发过来（第 4.2 节）
- 事件：delta 一段文字、done 结束（带 token 用量）、error 出错
"""

import json
import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from openai import APIError, AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import AI_MODEL, DEEPSEEK_API_KEY
from .db import Db, SessionLocal
from .errors import fail, success
from .models import AiChat, StudyDay, User
from .security import CurrentUser, is_admin

AI_UNLOCK_SECONDS = 10 * 60  # 累计学习满 10 分钟解锁问 AI


def study_seconds(session: Session, user: User) -> int:
    """这个用户同步到线上的累计学习秒数（前端每分钟同步一次，所以最多比本机少一分钟）。"""
    return session.scalar(select(func.coalesce(func.sum(StudyDay.seconds), 0)).where(StudyDay.user_id == user.id))


def ai_unlocked(session: Session, user: User) -> bool:
    return is_admin(user) or study_seconds(session, user) >= AI_UNLOCK_SECONDS


def ai_user(user: CurrentUser, session: Db) -> User:
    """没登录 401（CurrentUser 里就拦了）；登录了但学习时长不够 403，告诉他还差多少。"""
    if not ai_unlocked(session, user):
        minutes = study_seconds(session, user) // 60
        raise fail(403, f"累计学习满 {AI_UNLOCK_SECONDS // 60} 分钟才能用问 AI，现在是 {minutes} 分钟")
    return user


AiUser = Annotated[User, Depends(ai_user)]

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai")

# 没配 key 时不创建客户端，接口直接返回 503，其他接口照常能用
client = (
    AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com", timeout=60, max_retries=1)
    if DEEPSEEK_API_KEY
    else None
)

SYSTEM = """你是这份 Python / AI 应用开发学习笔记的助教，学习者正在读下面这一节。
回答规则：
- 用中文，先直接回答问题，再按需要补充；简短清楚，不要客套
- 学习者会引用笔记里的一段文字或代码来提问，优先结合这一节的上下文解释
- 需要举例时给能直接运行的 Python 代码，用 Markdown 代码块，输出写在注释里
- 不要用生活中的比喻来解释
- 笔记里没讲、或者你不确定的，直接说明

当前这一节：《{title}》
---
{text}
---"""


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class AiChatIn(BaseModel):
    chat_id: int | None = None  # 接着哪次对话问；新对话不传，后端建一条，用 chat 事件把 id 发回去
    section_id: str = Field(default="", max_length=64)
    section_title: str = Field(max_length=200)
    section_text: str = Field(max_length=60_000)  # 这一节的纯文字，最长的一节也在这个范围内
    quote: str | None = Field(default=None, max_length=3000)  # 选中的那段正文：拼进第一个问题，单独存一份方便历史里显示
    messages: Annotated[list[ChatMessage], Field(min_length=1, max_length=40)]  # 最后一条是这次的问题


def with_quote(quote: str, question: str) -> str:
    return f'我在这一节里选中了下面这段：\n"""\n{quote}\n"""\n\n{question}'


def open_chat(user: User, body: AiChatIn) -> int:
    """接着问就用原来那条（只能是自己的）；新对话建一条，标题是第一个问题。返回对话 id。"""
    with SessionLocal() as session:
        chat = session.get(AiChat, body.chat_id) if body.chat_id else None
        if chat is None or chat.user_id != user.id:
            chat = AiChat(
                user_id=user.id,
                section_id=body.section_id,
                section_title=body.section_title,
                title=body.messages[0].content[:200],
                quote=body.quote,
                messages=[],
            )
            session.add(chat)
        session.commit()
        return chat.id


def save_chat(chat_id: int, messages: list[dict]) -> None:
    """回答完（或中途停了、出错了）把整段对话存回去。流式响应开始后，请求自带的数据库会话已经关了，这里自己开一个。"""
    with SessionLocal() as session:
        chat = session.get(AiChat, chat_id)
        if chat is not None:
            chat.messages = messages
            chat.updated_at = func.now()
            session.commit()


def sse(event: str, data: dict) -> str:
    """一条 SSE 消息：event 行 + data 行 + 空行。"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def ai_chat(body: AiChatIn, request: Request, user: AiUser) -> StreamingResponse:
    if client is None:
        raise fail(503, "后端没有配置 DEEPSEEK_API_KEY")
    if body.messages[-1].role != "user":
        raise fail(422, "最后一条消息必须是问题")

    system = SYSTEM.format(title=body.section_title, text=body.section_text)
    history = [m.model_dump() for m in body.messages]  # 原样存进历史的（不带选中内容）
    to_model = [dict(m) for m in history]
    if body.quote:
        to_model[0]["content"] = with_quote(body.quote, to_model[0]["content"])  # 发给模型的：第一个问题带上选中的内容
    messages = [{"role": "system", "content": system}, *to_model]
    chat_id = open_chat(user, body)

    async def events():
        answer = ""
        finished = False
        yield sse("chat", {"id": chat_id})  # 先告诉前端这次对话的 id，下次追问带上它
        try:
            stream = await client.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},  # 最后一个片段带上 token 用量
                max_tokens=2000,
                extra_body={"thinking": {"type": "disabled"}},  # 解释笔记用不着思考，快一些也便宜
            )
            usage = None
            async for chunk in stream:
                if await request.is_disconnected():  # 前端点了停止或关了页面：不再往下读，也就不再计费
                    await stream.close()
                    break
                if chunk.usage:
                    usage = chunk.usage
                text = chunk.choices[0].delta.content if chunk.choices else None
                if text:
                    answer += text
                    yield sse("delta", {"text": text})
            else:
                finished = True
            if not finished:
                return
            yield sse(
                "done",
                {
                    "prompt_tokens": usage.prompt_tokens if usage else None,
                    "cache_hit_tokens": getattr(usage, "prompt_cache_hit_tokens", None),
                    "completion_tokens": usage.completion_tokens if usage else None,
                },
            )
        except APIError as e:
            logger.warning("DeepSeek 调用失败：%s", e)
            yield sse("error", {"msg": f"模型调用失败：{e.message}"})
        except Exception:
            logger.exception("问 AI 出错")
            yield sse("error", {"msg": "服务出错了，请稍后再试"})
        finally:
            # 不管是答完、中途停止还是出错，都把这次的问题和已经生成的部分存进历史
            reply = [{"role": "assistant", "content": answer, **({} if finished else {"stopped": True})}] if answer else []
            save_chat(chat_id, history + reply)

    # X-Accel-Buffering：让中间的代理别攒着，收到一段就转发一段
    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------- 历史对话：只能看、删自己的 ----------
@router.get("/chats")
def list_chats(user: CurrentUser, session: Db) -> dict:
    """最近 100 次对话，最新的在前；只返回列表要显示的字段，不带消息内容。"""
    rows = session.scalars(
        select(AiChat).where(AiChat.user_id == user.id).order_by(AiChat.updated_at.desc()).limit(100)
    ).all()
    return success([
        {
            "id": c.id,
            "title": c.title,
            "section_id": c.section_id,
            "section_title": c.section_title,
            "count": sum(1 for m in c.messages if m["role"] == "user"),  # 问了几次
            "updated_at": c.updated_at.isoformat() + ("" if c.updated_at.tzinfo else "+00:00"),
        }
        for c in rows
    ])


def own_chat(session: Session, user: User, chat_id: int) -> AiChat:
    chat = session.get(AiChat, chat_id)
    if chat is None or chat.user_id != user.id:  # 别人的对话也说「不存在」，不透露 id 有没有被用过
        raise fail(404, "这条对话不存在")
    return chat


@router.get("/chats/{chat_id}")
def get_chat(chat_id: int, user: CurrentUser, session: Db) -> dict:
    c = own_chat(session, user, chat_id)
    return success({"id": c.id, "section_id": c.section_id, "section_title": c.section_title, "quote": c.quote, "messages": c.messages})


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: int, user: CurrentUser, session: Db) -> dict:
    session.delete(own_chat(session, user, chat_id))
    return success()
