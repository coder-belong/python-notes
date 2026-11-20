import asyncio


async def fetch(name: str) -> str:
    await asyncio.sleep(1)
    return f"{name} 好了"


async def main() -> None:
    result = fetch("A")                 # 忘了写 await
    print(result)


asyncio.run(main())
# <coroutine object fetch at 0x10a635240>
# RuntimeWarning: coroutine 'fetch' was never awaited
