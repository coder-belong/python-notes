# limit_demo.py
import asyncio
import os
import time

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
limit = asyncio.Semaphore(3)                   # 最多同时 3 个请求


async def translate(word):
    async with limit:                          # 拿到名额才往下走，满了就排队等
        start = time.perf_counter()
        resp = await client.chat.completions.create(   # 异步调用，等的时候别的任务可以跑
            model="deepseek-flash",
            messages=[{"role": "user", "content": f"把「{word}」翻译成英文，只回答单词"}],
            extra_body={"thinking": {"type": "disabled"}},
        )
        print(word, resp.choices[0].message.content, f"{time.perf_counter() - start:.1f}s")
        return resp.choices[0].message.content


async def main():
    start = time.perf_counter()
    words = ["苹果", "香蕉", "西瓜", "葡萄", "橙子", "草莓"]
    results = await asyncio.gather(*(translate(w) for w in words))   # 6 个一起提交，同时只跑 3 个
    print(results, f"共 {time.perf_counter() - start:.1f}s")


asyncio.run(main())
# 苹果 Apple 0.5s
# 香蕉 banana 0.5s
# 西瓜 Watermelon 0.5s
# 橙子 Orange 0.4s
# 葡萄 grape 0.4s
# 草莓 strawberry 1.0s
# ['Apple', 'banana', 'Watermelon', 'grape', 'Orange', 'strawberry'] 共 1.5s
