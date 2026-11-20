import asyncio
import time


async def fetch(name: str) -> str:      # ① async def：定义异步函数
    await asyncio.sleep(1)              # ② await：在这里等，等的时候让别的任务先跑
    return f"{name} 好了"


async def main() -> None:
    start = time.perf_counter()
    # ③ gather：三个一起开始、一起等，全部完成后按顺序返回结果列表
    results = await asyncio.gather(fetch("A"), fetch("B"), fetch("C"))
    print(results)                                   # ['A 好了', 'B 好了', 'C 好了']
    print(f"用时 {time.perf_counter() - start:.1f}s")  # 用时 1.0s


asyncio.run(main())                     # ④ 程序入口：启动 main，整个程序只写一次
