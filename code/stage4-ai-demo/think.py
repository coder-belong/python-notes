# think.py：不关思考模式，看看多了什么
from llm import client

resp = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "user", "content": "一个笼子里有鸡和兔，共 10 个头、28 只脚，鸡兔各几只？只给答案"}],
)
msg = resp.choices[0].message
print(msg.content)                     # 鸡6只，兔4只。
print(msg.reasoning_content[:100])     # 思考过程，和 content 平级：
# We need answer only. Need compute. Let chicken x rabbit y. x+y=10, 2x+4y=28 => x+2y=14 => subtract x
print(resp.usage.completion_tokens, resp.usage.completion_tokens_details.reasoning_tokens)
# 76 67                                输出 76 个 token，其中 67 个是思考：答案本身只有 9 个

# 关掉思考模式，再问同一道题
resp = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "user", "content": "一个笼子里有鸡和兔，共 10 个头、28 只脚，鸡兔各几只？只给答案"}],
    extra_body={"thinking": {"type": "disabled"}},   # 关思考
)
msg = resp.choices[0].message
print(msg.content)                              # 鸡4只，兔6只。   经常答错，多跑几次试试
print(getattr(msg, "reasoning_content", None))  # None
print(resp.usage.completion_tokens)             # 8
