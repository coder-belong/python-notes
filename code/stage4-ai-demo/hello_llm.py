# hello_llm.py
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],   # 从环境变量读 key
    base_url="https://api.deepseek.com",      # 发到 DeepSeek，不写就是发到 OpenAI
)

resp = client.chat.completions.create(        # 发一次请求，等模型整段回答完才返回
    model="deepseek-flash",                   # 用哪个模型
    messages=[{"role": "user", "content": "用一句话介绍 FastAPI"}],   # 对话内容，下一节细讲
    extra_body={"thinking": {"type": "disabled"}},   # 关掉思考模式，见下面
)

print(resp.choices[0].message.content)        # 模型的回答
# FastAPI 是一个基于 Python 类型提示构建的现代、高性能 Web 框架，用于快速开发 API，支持自动生成交互式文档并具备异步能力。
print(resp.choices[0].finish_reason)          # stop：正常说完了
print(resp.usage.prompt_tokens, resp.usage.completion_tokens, resp.usage.total_tokens)
# 9 34 43                                     输入 9 个 token，输出 34 个，一共 43 个（按 token 收费）
