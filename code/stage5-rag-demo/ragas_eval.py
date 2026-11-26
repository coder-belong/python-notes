# ragas_eval.py：用 Ragas 给 RAG 打分：检索有没有找全（context recall）、回答有没有编（faithfulness）
import asyncio
import os

from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import ContextRecall, Faithfulness

from llm import MODEL, NO_THINKING, client
from load_docs import load_chunks
from rerank import rerank
from search import Searcher
from vector_search import HybridSearcher

# 打分也是让模型来判断，这里用 DeepSeek 当「评委」
judge = llm_factory(
    MODEL,
    client=AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com"),
    extra_body=NO_THINKING,   # 评委也关掉思考：快、便宜
)
recall_metric = ContextRecall(llm=judge)
faith_metric = Faithfulness(llm=judge)

# 评测集：问题 + 标准答案（人写的，用来判断检索到的资料够不够回答）
DATA = [
    ("店里有网吗", "有，店里提供免费 Wi-Fi，也有插座。"),
    ("充的钱能退吗", "储值卡余额不能退现金，但可以转赠给其他会员。"),
    ("超过 30 分钟送到能退款吗", "外卖超过预计送达时间 30 分钟，可以申请全额退款。"),
    ("办会员要钱吗", "不收费，在小程序里用手机号注册就是普通会员。"),
    ("金卡会员有哪些优惠", "生日月送一杯饮品，买饮品打九折。"),
    ("会员积分能换什么", "100 积分换中杯美式，300 积分换任意一杯饮品。"),
]

chunks = load_chunks()
bm25, hybrid = Searcher(chunks), HybridSearcher(chunks)
RETRIEVERS = {
    "关键词": lambda q: [c for _, c in bm25.search(q, k=2)],
    "混合 + 重排": lambda q: [c for _, c in rerank(q, hybrid.search(q, k=5), k=2)],
}
PROMPTS = {
    "只按资料": "你是豆豆咖啡的客服，只根据 <docs> 里的资料回答，一两句话；资料里没有的就说不清楚。",
    "不限制": "你是豆豆咖啡的热情客服，参考 <docs> 回答，尽量把答案说得完整、丰富，可以补充你知道的常见做法。",
}


def answer(system: str, question: str, docs: list[str]) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system + "\n<docs>\n" + "\n".join(docs) + "\n</docs>"},
                  {"role": "user", "content": question}],
        extra_body=NO_THINKING,
    )
    return resp.choices[0].message.content


async def run(retriever: str, prompt: str) -> None:
    recalls, faiths = [], []
    for q, ref in DATA:
        docs = [c.title + "：" + c.text for c in RETRIEVERS[retriever](q)] or ["（没有检索到相关资料）"]   # 一段都没搜到时 Ragas 不接受空列表
        resp = answer(PROMPTS[prompt], q, docs)
        r = await recall_metric.ascore(user_input=q, retrieved_contexts=docs, reference=ref)
        f = await faith_metric.ascore(user_input=q, response=resp, retrieved_contexts=docs)
        recalls.append(r.value)
        faiths.append(f.value)
    avg = lambda xs: sum(xs) / len(xs)  # noqa: E731
    print(f"检索={retriever:<6} 提示词={prompt:<4}  召回 {avg(recalls):.2f}  忠实度 {avg(faiths):.2f}")


async def main() -> None:
    await run("关键词", "只按资料")
    await run("混合 + 重排", "只按资料")
    await run("混合 + 重排", "不限制")


asyncio.run(main())
