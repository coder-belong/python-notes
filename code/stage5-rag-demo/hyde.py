# hyde.py：HyDE：先让模型写一段「假想的答案」，用它去搜，而不是用问题本身去搜
import numpy as np

from embed import embed
from llm import MODEL, NO_THINKING, client
from load_docs import load_chunks


def fake_answer(question: str) -> str:
    """让模型照着「咖啡店规定」的口吻编一段答案：不用对，只要用词像文档就行。"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"假设你是咖啡店的规章文档，用一两句话回答：{question}"}],
        max_tokens=80,
        extra_body=NO_THINKING,
    )
    return resp.choices[0].message.content


chunks = {c.title: c for c in load_chunks()}
for q, title in [("店里有网吗", "自习"), ("充的钱能退吗", "储值卡"), ("办会员要钱吗", "怎么成为会员")]:
    target = np.array(embed([title + "：" + chunks[title].text])[0])
    hyde = fake_answer(q)
    sims = []
    for text in (q, hyde):
        v = np.array(embed([text])[0])
        sims.append(float(v @ target / (np.linalg.norm(v) * np.linalg.norm(target))))   # 和正确那段的余弦相似度
    print(f"{q}：问题本身 {sims[0]:.2f} → 假想答案 {sims[1]:.2f}")
    print(f"    假想答案：{hyde}")
