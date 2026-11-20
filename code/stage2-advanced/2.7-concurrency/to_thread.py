import asyncio
import time


def slow_sync(name: str) -> str:    # 一个只有同步版本的慢函数
    time.sleep(1)
    return f"{name} 完成"


async def main() -> None:
    start = time.perf_counter()
    # 两个慢函数分别放到两个线程里跑，await 等结果；等的时候不会卡住其他协程
    results = await asyncio.gather(
        asyncio.to_thread(slow_sync, "A"),
        asyncio.to_thread(slow_sync, "B"),
    )
    print(results)                                     # ['A 完成', 'B 完成']
    print(f"用时 {time.perf_counter() - start:.1f}s")    # 用时 1.0s，两个一起等，不是 2 秒


asyncio.run(main())
