# rag.py
from load_docs import load_chunks
from llm import MODEL, NO_THINKING, client
from search import Searcher

searcher = Searcher(load_chunks())   # 启动时切好文档、建好索引，之后每次提问直接查


def chat(system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        extra_body=NO_THINKING,
    )
    return resp.choices[0].message.content


REWRITE = """把用户的问题改写成适合搜索的关键词，用空格隔开，只输出关键词。
- 口语换成书面说法，比如「狗狗」写成「宠物」
- 结合对话历史，把「那」「它」这种指代换成具体的东西"""


def rewrite(question: str, history: str = "") -> str:
    return chat(REWRITE, f"<history>{history}</history>\n<question>{question}</question>")


ANSWER = """你是豆豆咖啡的客服，只根据 <docs> 里的资料回答，回答简短。
每句话后面用 [编号] 标出依据的是哪段资料；资料里没有的，就说不清楚，请联系门店。"""


def answer(question: str, history: str = "") -> None:
    query = rewrite(question, history)
    hits = searcher.search(query, k=2)
    # 给每段资料编号，模型回答时引用编号；编号 → 出处，最后展示给用户
    docs = "\n".join(f"[{i}] {c.title}：{c.text}" for i, (_, c) in enumerate(hits, 1))   # enumerate(..., 1)：编号从 1 开始
    reply = chat(ANSWER, f"<docs>\n{docs}\n</docs>\n问题：{question}")
    print("问题：", question)
    print("搜索：", query)
    print("回答：", reply)
    for i, (_, c) in enumerate(hits, 1):
        print(f"   [{i}] {c.source} · {c.title}")
    print()


if __name__ == "__main__":   # 直接运行才执行；eval_search.py import 它时不执行
    answer("我家狗狗能进来吗")                                     # 口语：改写后才搜得到
    answer("那周末几点关门？", history="用户：工作日几点开门？\n客服：7:30 开门。")   # 多轮：「那」指的是营业时间
    answer("可以用支付宝付款吗？")                                  # 资料里没有
