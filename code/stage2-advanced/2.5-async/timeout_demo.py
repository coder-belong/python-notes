import asyncio


async def slow() -> str:
    await asyncio.sleep(3)              # 模拟一个要 3 秒的请求
    return "好了"


async def main() -> None:
    try:
        async with asyncio.timeout(1):  # 里面的代码超过 1 秒就取消
            print(await slow())
    except TimeoutError:
        print("超过 1 秒，不等了")


asyncio.run(main())                     # 超过 1 秒，不等了
