import asyncio
import time

import httpx


async def main() -> None:
    async with httpx.AsyncClient(base_url="https://httpbin.org", timeout=10) as client:   # 异步版的 Client，用 async with
        start = time.perf_counter()                       # 记下开始时间
        for _ in range(3):                                # 一个一个发：等完一个再发下一个
            await client.get("/delay/1")                  # 这个接口故意等 1 秒才返回
        print(f"一个一个发：{time.perf_counter() - start:.1f}s")

        start = time.perf_counter()
        requests = [client.get("/delay/1") for _ in range(3)]   # 准备 3 个请求；没 await，还没发出去（_ 表示用不到循环变量）
        responses = await asyncio.gather(*requests)       # *requests 拆开传入，等于 gather(请求1, 请求2, 请求3)：一起发、一起等
        print([r.status_code for r in responses])         # 结果顺序和传入顺序一样
        print(f"同时发：{time.perf_counter() - start:.1f}s")


asyncio.run(main())
# 一个一个发：4.5s
# [200, 200, 200]
# 同时发：1.8s
