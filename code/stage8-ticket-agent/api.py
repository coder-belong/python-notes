# api.py：接口：提问（SSE 推每一步）、确认高风险操作后接着跑（SSE）、查任务记录
import json
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

import agent
from db import Task, engine, init_db

init_db()
app = FastAPI()


class AskIn(BaseModel):
    user: str            # 真实项目里从登录 token 里取（3.13 节），这里简化成直接传
    question: str


class ConfirmIn(BaseModel):
    approve: bool


def sse(events: Iterator[dict]) -> StreamingResponse:
    def gen():
        for e in events:
            kind = e.pop("event")
            yield f"event: {kind}\ndata: {json.dumps(e, ensure_ascii=False)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/tasks")
def ask(body: AskIn) -> StreamingResponse:
    return sse(agent.start(body.user, body.question))


@app.post("/tasks/{task_id}/confirm")
def confirm(task_id: int, body: ConfirmIn) -> StreamingResponse:
    return sse(agent.resume(task_id, body.approve))


@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    with Session(engine) as s:
        t = s.get(Task, task_id)
        return {"status": t.status, "answer": t.answer, "steps": t.steps}
