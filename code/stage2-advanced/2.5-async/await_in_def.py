import asyncio


async def fetch(name: str) -> str:
    await asyncio.sleep(1)
    return f"{name} 好了"


def main() -> None:                     # 普通 def，不是 async def
    result = await fetch("A")
# SyntaxError: 'await' outside async function
