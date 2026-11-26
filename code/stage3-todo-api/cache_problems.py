# cache_problems.py：缓存三大问题：穿透、击穿、雪崩。用一个「假数据库」数被查了几次
import json
import random
import threading
import time

from redis import Redis

r = Redis.from_url("redis://localhost:6379/3", decode_responses=True)   # 演示用 3 号库
db_hits = 0
lock = threading.Lock()
PRODUCTS = {i: {"id": i, "name": f"商品{i}"} for i in range(1, 101)}   # 数据库里只有 1～100 号


def query_db(pid: int) -> dict | None:
    """假装查数据库：每次 50 毫秒，并且记一次数。"""
    global db_hits
    with lock:
        db_hits += 1
    time.sleep(0.05)
    return PRODUCTS.get(pid)


# ---------- 普通写法：缓存没有就查数据库 ----------
def get_naive(pid: int) -> dict | None:
    if (cached := r.get(f"p:{pid}")) is not None:
        return json.loads(cached)
    data = query_db(pid)
    if data:                                          # 查不到的不缓存
        r.set(f"p:{pid}", json.dumps(data), ex=60)
    return data


# ---------- 改进：缓存空值 + 互斥锁 + 随机过期时间 ----------
def get_safe(pid: int) -> dict | None:
    key = f"p:{pid}"
    for _ in range(50):
        if (cached := r.get(key)) is not None:
            return json.loads(cached) if cached != "null" else None     # 穿透：查不到也缓存一个 "null"
        # 击穿：只让一个请求去查数据库，其他的等它写好缓存。SET NX：key 不存在才设置成功，就是一把锁
        if r.set(f"lock:{key}", "1", nx=True, ex=5):
            try:
                if (cached := r.get(key)) is not None:                    # 拿到锁后再看一眼：可能别人刚写好
                    return json.loads(cached) if cached != "null" else None
                data = query_db(pid)
                ttl = 60 + random.randint(0, 30)                         # 雪崩：过期时间加随机数，别同时过期
                r.set(key, json.dumps(data) if data else "null", ex=ttl if data else 30)
                return data
            finally:
                r.delete(f"lock:{key}")
        time.sleep(0.02)                                                 # 没抢到锁：等一会儿再看缓存
    return query_db(pid)


def burst(fn, pid: int, n: int) -> None:
    """模拟同一时刻 n 个请求查同一个商品。"""
    threads = [threading.Thread(target=fn, args=(pid,)) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def run(title: str, action) -> None:
    global db_hits
    r.flushdb()
    db_hits = 0
    action()
    print(f"{title}：数据库被查了 {db_hits} 次")


print("--- 穿透：反复查一个不存在的商品 999（比如被人恶意刷接口）")
run("普通写法", lambda: [get_naive(999) for _ in range(20)])
run("缓存空值", lambda: [get_safe(999) for _ in range(20)])

print("--- 击穿：热门商品 1 的缓存刚过期，同时来了 50 个请求")
run("普通写法", lambda: burst(get_naive, 1, 50))
run("互斥锁  ", lambda: burst(get_safe, 1, 50))

print("--- 雪崩：一批缓存同一时刻写进去（比如服务刚启动时预热）")
r.flushdb()
for i in range(1, 101):
    r.set(f"fixed:{i}", "x", ex=60)                                      # 普通写法：都是 60 秒
    r.set(f"random:{i}", "x", ex=60 + random.randint(0, 30))             # 改进：60～90 秒随机
fixed = {r.ttl(f"fixed:{i}") for i in range(1, 101)}
spread = [r.ttl(f"random:{i}") for i in range(1, 101)]
print(f"普通写法：100 个 key 剩余时间都是 {sorted(fixed)} 秒 → 同一秒一起失效，请求一起打到数据库")
print(f"随机过期：剩余时间分散在 {min(spread)}～{max(spread)} 秒，共 {len(set(spread))} 种 → 失效时间错开了")
