# worker.py：任务队列的「干活的人」：从 Redis 里取任务、执行，结果写回 Redis
import asyncio
import json

from arq import Retry
from arq.connections import RedisSettings

REDIS = RedisSettings(host="localhost", port=6379, database=2)   # 单独用 2 号库，不和别的数据混


async def make_report(ctx: dict, topic: str) -> str:
    """模拟一个要跑很久的任务：比如让模型读 100 份文档写总结。分 4 步，每步汇报进度。"""
    job_id, redis = ctx["job_id"], ctx["redis"]
    if ctx["job_try"] == 1 and topic == "会失败一次":
        raise Retry(defer=1)                      # 第一次故意失败：1 秒后自动重试（比如模型接口限流）
    for step in range(1, 5):
        await asyncio.sleep(1)                    # 真实项目里这里是调模型、读文件
        await redis.set(f"progress:{job_id}", json.dumps({"step": step, "total": 4}), ex=3600)
    return f"《{topic}》报告写好了（第 {ctx['job_try']} 次尝试成功）"


class WorkerSettings:                             # arq 的约定：worker 的配置写成这样一个类
    functions = [make_report]
    redis_settings = REDIS
    max_tries = 3                                 # 最多试 3 次
    job_timeout = 600                             # 单个任务最多跑 10 分钟
