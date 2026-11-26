# app.py：接口只负责「接单」：把任务放进队列马上返回，再提供一个查进度的接口
import json
from contextlib import asynccontextmanager

from arq import create_pool
from arq.jobs import Job, JobStatus
from fastapi import FastAPI
from pydantic import BaseModel

from worker import REDIS

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await create_pool(REDIS)   # 启动时连接 Redis（2.8 节的 lifespan），放进 app.state 供各个接口用
    yield
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)


class ReportIn(BaseModel):
    topic: str


@app.post("/reports")
async def create_report(body: ReportIn) -> dict:
    job = await app.state.redis.enqueue_job("make_report", body.topic)   # 放进队列，不等它做完
    return {"job_id": job.job_id}


@app.get("/reports/{job_id}")
async def get_report(job_id: str) -> dict:
    redis = app.state.redis
    job = Job(job_id, redis)
    status = await job.status()                   # queued 排队中 / in_progress 进行中 / complete 完成
    out: dict = {"status": status.value}
    if progress := await redis.get(f"progress:{job_id}"):
        out["progress"] = json.loads(progress)
    if status == JobStatus.complete:
        info = await job.result_info()
        out["result"] = info.result if info.success else f"失败：{info.result}"
        out["tries"] = info.job_try
    return out
