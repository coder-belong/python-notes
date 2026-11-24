# app/services/login_limit.py（3.20 新建：登录失败次数限制）
from __future__ import annotations

from redis import Redis

from app.errors import fail

MAX_FAILS = 5                 # 最多连续错几次
WINDOW = 10 * 60              # 在多长时间内（秒）：10 分钟


def _key(username: str) -> str:
    return f"login_fail:{username}"   # 每个用户名一个计数器，key 加前缀，一看就知道是干什么的


def check(r: Redis, username: str) -> None:
    """登录前检查：错太多次就直接拒绝，连密码都不验。"""
    fails = int(r.get(_key(username)) or 0)    # 没有这个 key 时 get 返回 None，当成 0
    if fails >= MAX_FAILS:
        minutes = (r.ttl(_key(username)) + 59) // 60   # 还要等几分钟：剩余秒数向上取整
        raise fail(429, f"密码错误次数太多，请 {minutes} 分钟后再试")


def record_fail(r: Redis, username: str) -> None:
    """密码错了：计数 +1；第一次错的时候设置过期时间，10 分钟后自动清零。"""
    fails = r.incr(_key(username))             # INCR：key 不存在时先当成 0，再加 1，返回加完的值
    if fails == 1:
        r.expire(_key(username), WINDOW)       # 只在第一次设：之后再错不会延长时间


def reset(r: Redis, username: str) -> None:
    """登录成功：清掉计数。"""
    r.delete(_key(username))
