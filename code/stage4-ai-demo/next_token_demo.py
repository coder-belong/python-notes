# next_token_demo.py
import math

from llm import MODEL, NO_THINKING, client


def show(prompt: str, n: int) -> None:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=n,       # 只看前几个 token
        logprobs=True,      # 返回每个 token 的概率
        top_logprobs=3,     # 每个位置再给出概率最高的 3 个候选
        extra_body=NO_THINKING,
    )
    for item in resp.choices[0].logprobs.content:   # 生成出来的每个 token
        # logprob 是概率取了对数，math.exp 换回 0～1 的概率
        cands = "  ".join(f"{c.token!r} {math.exp(c.logprob):.0%}" for c in item.top_logprobs)
        print(f"选了 {item.token!r:8}  候选：{cands}")
    print()


show("接着写下一句，只输出这一句：床前明月光，", 6)   # 答案很确定
show("给一家奶茶店起个名字，只输出名字", 4)          # 答案不确定
