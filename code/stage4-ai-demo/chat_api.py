# chat_api.py
import json
import os
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI()
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")   # 接口里用异步的


class ChatIn(BaseModel):
    question: str


def sse(event: str, data: dict) -> str:
    """拼一个 SSE 事件：event 一行、data 一行、最后一个空行。"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
async def chat_stream(body: ChatIn, request: Request) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:   # 生成器：每 yield 一次，就往响应里写一段
        stream = await client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": body.question}],
            stream=True,
            extra_body={"thinking": {"type": "disabled"}},
        )
        parts: list[str] = []
        finished = False
        try:
            async for chunk in stream:          # 异步版的 for：模型每给一个片段走一次
                if await request.is_disconnected():   # ① 前端断开了（关页面、点了停止）：不用再往下读
                    break
                text = chunk.choices[0].delta.content if chunk.choices else None
                if text:
                    parts.append(text)
                    yield sse("delta", {"text": text})   # ② 片段推给前端
            else:                               # for 正常走完（没有 break）才会进 else
                finished = True
                yield sse("done", {"length": len("".join(parts))})   # ③ 告诉前端：说完了
        except Exception as e:
            yield sse("error", {"msg": str(e)})  # ④ 中途出错：响应头已经发出去了，只能用事件告诉前端
        finally:
            await stream.close()                # ⑤ 不管怎样都关掉和模型的连接，不再继续生成、继续收费
            # ⑥ 在这里保存结果：真实项目里写进数据库，完整的还是中途断开的都要记下来
            print(f"保存回答：{'完整' if finished else '中途断开'}，{len(''.join(parts))} 个字", flush=True)

    return StreamingResponse(events(), media_type="text/event-stream")   # 把生成器包成 SSE 响应
