# models_demo.py
import os
import time

from openai import OpenAI

# 每家的地址和 key 写在配置里；它们都兼容 OpenAI 的接口格式，代码不用改
PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com", "key_env": "DEEPSEEK_API_KEY"},
    "qwen": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "key_env": "DASHSCOPE_API_KEY"},
    "kimi": {"base_url": "https://api.moonshot.cn/v1", "key_env": "MOONSHOT_API_KEY"},
}


def make_client(provider: str) -> OpenAI:
    cfg = PROVIDERS[provider]
    return OpenAI(api_key=os.environ[cfg["key_env"]], base_url=cfg["base_url"])   # 只有地址和 key 不同


def ask(provider: str, model: str, question: str, **extra) -> None:
    client = make_client(provider)
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": question}], **extra   # **extra：把额外参数原样传进去
    )
    u = resp.usage
    print(f"{model}：{time.perf_counter() - start:.1f}s，输出 {u.completion_tokens} token")
    print("   ", resp.choices[0].message.content.replace("\n", " ")[:80])


Q = "一个水池，进水管 3 小时注满，出水管 5 小时放完，两管同时开几小时注满？只给答案和一句算式。"
NO_THINKING = {"extra_body": {"thinking": {"type": "disabled"}}}

ask("deepseek", "deepseek-flash", Q, **NO_THINKING)    # 快、便宜：日常问答、分类、提取
ask("deepseek", "deepseek-v4-pro", Q, **NO_THINKING)   # 更强、更贵：难题、写长代码
ask("deepseek", "deepseek-v4-pro", Q)                  # 再打开思考：更慢，但难题更稳
