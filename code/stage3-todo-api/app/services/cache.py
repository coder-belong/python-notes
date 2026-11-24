# app/services/cache.py（3.20 新建：把查询结果缓存一会儿）
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from redis import Redis


def cached(r: Redis, key: str, seconds: int, load: Callable[[], Any]) -> Any:
    """先查缓存，有就直接返回；没有才调 load() 去查数据库，结果存进缓存，seconds 秒后自动过期。"""
    hit = r.get(key)
    if hit is not None:                        # 缓存里有：不查数据库
        return json.loads(hit)                 # Redis 里存的是字符串，转回 Python 对象
    value = load()                             # 缓存里没有：真的去查
    r.set(key, json.dumps(value, ensure_ascii=False, default=str), ex=seconds)   # 存成 JSON 字符串，ex：几秒后过期
    return value
