# app/redis_client.py（3.20 新建：连 Redis，和 db.py 的写法一样）
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from redis import Redis

from app.config import settings

redis = Redis.from_url(settings.redis_url, decode_responses=True)   # decode_responses：取出来的是 str，不是 bytes


def get_redis() -> Redis:
    """依赖：接口里拿到 Redis 客户端。写成依赖，测试时能换成测试用的库（和 3.11 换数据库一样）。"""
    return redis


RedisDep = Annotated[Redis, Depends(get_redis)]   # 接口里写 r: RedisDep
