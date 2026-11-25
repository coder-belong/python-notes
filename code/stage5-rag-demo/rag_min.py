# rag_min.py
from pathlib import Path

from load_docs import read_text   # 读文件成文字，5.2 节写
from llm import MODEL, NO_THINKING, client


def ask(question: str, context: str = "") -> None:
    system = "你是豆豆咖啡的客服，回答简短。"
    if context:   # 有资料就放进 system，并要求只按资料回答
        system += f"只根据 <docs> 里的资料回答；资料里没有的，就说不清楚，请联系门店。\n<docs>\n{context}\n</docs>"
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
        extra_body=NO_THINKING,
    )
    print(resp.usage.prompt_tokens, resp.choices[0].message.content.replace("\n", " "))


Q = "积分多久过期？外卖晚了能退款吗？"

# ① 什么资料都不给：模型只能编
ask(Q)

# ② 把全部文档塞进去：答对了
all_docs = "\n\n".join(read_text(p) for p in sorted(Path("docs").iterdir()))
ask(Q, all_docs)

# ③ 资料里没有的问题
ask("可以用支付宝付款吗？", all_docs)
