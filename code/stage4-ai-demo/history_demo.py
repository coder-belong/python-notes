# history_demo.py
from llm import MODEL, NO_THINKING, client


def ask(messages):
    resp = client.chat.completions.create(model=MODEL, messages=messages, extra_body=NO_THINKING)
    return resp.choices[0].message.content, resp.usage.prompt_tokens   # 回答、这次输入了多少 token


print(ask([{"role": "user", "content": "我叫什么？"}]))
# ('你好！😊 从我们的对话中，我并不知道你的名字——你还没有告诉我呢。...', 7)

history = [{"role": "system", "content": "回答不超过 20 个字。"}]
for text in ["我叫小林，在学 Python", "我叫什么？", "我在学什么？"]:
    history.append({"role": "user", "content": text})          # ① 用户的话加进历史
    answer, prompt_tokens = ask(history)                       # ② 整个历史发过去
    history.append({"role": "assistant", "content": answer})   # ③ 模型的回答也加进历史，下一轮带上
    print(text, "→", answer, prompt_tokens)
# 我叫小林，在学 Python → 你好小林！Python 学习加油，有什么问题可以问我。 18
# 我叫什么？ → 你叫小林。 38
# 我在学什么？ → 你在学 Python。 50
print(len(history))                                            # 7：1 条 system + 3 轮 × 2 条
