# agent_api.py：把 Agent 每一步都用 SSE 推给前端（4.6 节的写法）
import json
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent import MAX_STEPS, RISKY, SYSTEM, run_tool
from llm import MODEL, NO_THINKING, client
from tools import TOOLS

app = FastAPI()


class TaskIn(BaseModel):
    task: str


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def agent_events(task: str) -> Iterator[str]:
    """和 agent.py 的 run_agent 一样的循环，只是每做一件事就 yield 一个事件，而不是 print。"""
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}]
    try:
        for step in range(1, MAX_STEPS + 1):
            yield sse("thinking", {"step": step})                  # 前端显示「思考中…」
            msg = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING
            ).choices[0].message
            messages.append(msg)
            if not msg.tool_calls:
                yield sse("final", {"text": msg.content})          # 最终回答
                return
            for call in msg.tool_calls:
                name, args = call.function.name, call.function.arguments
                if name in RISKY:                                  # 网页上不能 input()：先停下，让前端弹确认框
                    yield sse("confirm", {"tool": name, "args": json.loads(args)})
                    return
                yield sse("tool_start", {"tool": name, "args": json.loads(args)})   # 前端显示「正在查天气…」
                ok, result = run_tool(name, args, confirm=lambda *_: False)
                yield sse("tool_end", {"tool": name, "ok": ok, "result": result})
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        yield sse("final", {"text": "步数用完了，任务没完成"})
    except Exception as e:
        yield sse("error", {"msg": str(e)})


@app.post("/agent/stream")
def agent_stream(body: TaskIn) -> StreamingResponse:
    return StreamingResponse(agent_events(body.task), media_type="text/event-stream")
