# token_demo.py
from llm import MODEL, NO_THINKING, client


def count_tokens(text):
    resp = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": text}], max_tokens=1, extra_body=NO_THINKING,
    )                                          # max_tokens=1：只想看输入有多少 token，回答只要 1 个
    return resp.usage.prompt_tokens


zh = "今天天气不错，我们去公园散步吧。" * 10
en = "The weather is nice today, let's go for a walk in the park. " * 10
print(len(zh), count_tokens(zh))   # 160 94    160 个字 → 94 个 token，约 0.6
print(len(en), count_tokens(en))   # 600 165   600 个字母 → 165 个 token，约 0.3


resp = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": "详细介绍一下 FastAPI"}], max_tokens=30, extra_body=NO_THINKING,
)
print(resp.choices[0].message.content)
# # FastAPI 详细介绍
#
# ## 一、什么是 FastAPI
#
# FastAPI 是一个现代、快速（高性能）的 Python Web 框架，
print(resp.choices[0].finish_reason, resp.usage.completion_tokens)   # length 30   话没说完就被截断了
