# sys_demo.py
from llm import MODEL, NO_THINKING, client

question = {"role": "user", "content": "Python 和 JavaScript 有什么区别？"}

# ① 不加 system：模型按自己的习惯回答
resp = client.chat.completions.create(model=MODEL, messages=[question], extra_body=NO_THINKING)
print(resp.choices[0].message.content[:60])   # 只看开头：写了一篇带标题、带表格的长文
# # Python 和 JavaScript 的区别
#
# Python 和 JavaScript 是两门非常流行但设计理念差
print(resp.usage.completion_tokens)           # 765

# ② 加 system：按你定的规则回答
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是编程老师。回答不超过 30 个字，不用 Markdown。"},
        question,
    ],
    extra_body=NO_THINKING,
)
print(resp.choices[0].message.content)        # Python 重可读和数据分析，JS 重浏览器和网页交互。
print(resp.usage.completion_tokens)           # 16：输出少了，钱也少了

# System Prompt 不会被记住：每次请求都要带上
system = {"role": "system", "content": "你是编程老师。回答不超过 30 个字，不用 Markdown。"}
history = [
    {"role": "user", "content": "Python 和 JavaScript 有什么区别？"},
    {"role": "assistant", "content": "Python 重可读和数据分析，JS 重浏览器和网页交互。"},
    {"role": "user", "content": "那 Go 呢？"},
]
resp = client.chat.completions.create(model=MODEL, messages=[system, *history], extra_body=NO_THINKING)
print(resp.choices[0].message.content, resp.usage.completion_tokens)       # 带 system：简短
resp = client.chat.completions.create(model=MODEL, messages=history, extra_body=NO_THINKING)
print(resp.choices[0].message.content[:30], resp.usage.completion_tokens)  # 不带 system：长文
