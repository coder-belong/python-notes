# error_demo.py
import os
import time

import openai
from openai import OpenAI

from llm import MODEL, NO_THINKING

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
    timeout=30,        # 一次请求最多等 30 秒（默认等 600 秒，太长了）
    max_retries=2,     # 超时、连不上、429、5xx 时自动重试 2 次（默认就是 2）
)
print(client.timeout, client.max_retries)   # 30 2

msgs = [{"role": "user", "content": "写一篇 500 字的文章"}]
start = time.perf_counter()
try:
    client.chat.completions.create(model=MODEL, messages=msgs, extra_body=NO_THINKING, timeout=1)   # 单次请求也能覆盖：故意只等 1 秒
except openai.APITimeoutError as e:
    print(type(e).__name__, e, round(time.perf_counter() - start, 1))
# APITimeoutError Request timed out. 4.8    一共试了 3 次（1 次 + 重试 2 次），每次 1 秒，中间还等了一会儿


bad = OpenAI(api_key="sk-wrong", base_url="https://api.deepseek.com")   # 故意用错的 key
try:
    bad.chat.completions.create(model=MODEL, messages=msgs)
except openai.AuthenticationError as e:
    print(e.status_code, e.message)
# 401 Error code: 401 - Authentication Fails, Your api key: ****rong is invalid (request_id: ...)

try:
    client.chat.completions.create(model="deepseek-xxx", messages=msgs)   # 故意写错模型名
except openai.BadRequestError as e:
    print(e.status_code, e.message)
# 400 Error code: 400 - The supported API model names are deepseek-flash, deepseek-v4-pro, but you passed deepseek-xxx. (request_id: ...)
