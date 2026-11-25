# chat_web.py：多轮对话的流式接口 + 一个前端页面（4.12 节）
import json
import os
from collections.abc import AsyncIterator
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

app = FastAPI()
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")


class Message(BaseModel):
    role: Literal["user", "assistant"]   # 前端只能传这两种，不能自己塞 system（4.11 节）
    content: str


class ChatIn(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=40)   # 前端把这个会话的历史全传上来（4.2 节：模型没有记忆）


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
async def chat_stream(body: ChatIn, request: Request) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        system = {"role": "system", "content": "你是 Python 学习助手，用 Markdown 回答，代码放进代码块。"}
        stream = await client.chat.completions.create(
            model="deepseek-flash",
            messages=[system, *[m.model_dump() for m in body.messages]],
            stream=True,
            extra_body={"thinking": {"type": "disabled"}},
        )
        try:
            async for chunk in stream:
                if await request.is_disconnected():
                    break
                text = chunk.choices[0].delta.content if chunk.choices else None
                if text:
                    yield sse("delta", {"text": text})
            else:
                yield sse("done", {})
        except Exception as e:
            yield sse("error", {"msg": str(e)})
        finally:
            await stream.close()

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/")
def index() -> FileResponse:
    return FileResponse("web/index.html")   # 页面和接口同一个地址，不用处理跨域（3.16 节）
