# stream_demo.py
from llm import MODEL, NO_THINKING, client

# stream 可以当成一个「片段列表」来理解，只是片段是边生成边送过来的，for 的时候一个一个读：
# [
#     chunk(choices=[Choice(delta=Delta(content=""))]),      第 1 个：常常是空字符串
#     chunk(choices=[Choice(delta=Delta(content="1"))]),     第 2 个：一两个字
#     chunk(choices=[Choice(delta=Delta(content="."))]),
#     ...
#     chunk(choices=[], usage=CompletionUsage(...)),          最后一个：没有文字，只有 usage
# ]
stream = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "用三句话介绍 Python"}],
    stream=True,                               # 流式：边生成边返回
    stream_options={"include_usage": True},    # 最后多给一个片段，带上 usage（流式默认不给）
    extra_body=NO_THINKING,
)

parts = []                                     # 同时把片段攒起来，最后拼成完整回答（存数据库等要用）
for i, chunk in enumerate(stream):             # 每生成一点，循环就走一次
    # 这个片段的文字：在 delta.content，不是 message.content；最后那个只带 usage 的片段 choices 是空的
    text = chunk.choices[0].delta.content if chunk.choices else None
    if text:                                   # 第一个片段常常是空字符串，和 None 一起跳过
        print(text, end="", flush=True)        # 收到就打印：end="" 不换行，flush=True 立刻显示出来
        parts.append(text)
    if chunk.usage:                            # 最后那个片段：只有 usage，回答已经打印完了
        print("\nusage:", chunk.usage.prompt_tokens, chunk.usage.completion_tokens, "chunks:", i + 1)
answer = "".join(parts)                        # 完整回答
