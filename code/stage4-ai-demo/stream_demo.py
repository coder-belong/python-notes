# stream_demo.py
from llm import MODEL, NO_THINKING, client

stream = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "用三句话介绍 Python"}],
    stream=True,                               # 流式：边生成边返回
    stream_options={"include_usage": True},    # 最后多给一个片段，带上 usage（流式默认不给）
    extra_body=NO_THINKING,
)

parts = []                                     # 把片段攒起来，最后拼成完整回答
for i, chunk in enumerate(stream):             # 每生成一点，循环就走一次
    if i < 3:                                  # 看看前 3 个片段装的是什么
        print(repr(chunk.choices[0].delta.content) if chunk.choices else None)
    if chunk.choices and chunk.choices[0].delta.content:   # 片段里的文字在 delta.content，不是 message.content
        parts.append(chunk.choices[0].delta.content)
    if chunk.usage:                            # 最后那个片段：choices 是空的，只有 usage
        print("usage:", chunk.usage.prompt_tokens, chunk.usage.completion_tokens, "chunks:", i + 1)
print("".join(parts))
