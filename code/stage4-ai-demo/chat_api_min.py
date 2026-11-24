# chat_api_min.py：最小版，只管把片段推给前端（4.6 节）
import json
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI()                               # 创建 FastAPI 应用对象
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")   # 创建异步客户端对象：接口里用异步的


class ChatIn(BaseModel):
    question: str


def sse(event: str, data: dict) -> str:
    """拼一个 SSE 事件：event 一行、data 一行、最后一个空行。"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
async def chat_stream(body: ChatIn) -> StreamingResponse:
    async def events():                       # 生成器：每 yield 一次，就往响应里写一段
        stream = await client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": body.question}],
            stream=True,
            extra_body={"thinking": {"type": "disabled"}},
        )
        async for chunk in stream:            # 异步版的 for：模型每给一个片段走一次
            text = chunk.choices[0].delta.content if chunk.choices else None
            if text:
                yield sse("delta", {"text": text})   # 片段推给前端

    return StreamingResponse(events(), media_type="text/event-stream")   # 把生成器包成 SSE 响应
