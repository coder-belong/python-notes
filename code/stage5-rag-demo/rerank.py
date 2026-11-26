# rerank.py：先粗搜出 5 段，再用重排模型逐段打分，挑出最相关的
from fastembed.rerank.cross_encoder import TextCrossEncoder

from load_docs import Chunk

# 重排模型：把「问题 + 一段资料」一起读进去打分，比向量相似度准，但慢，所以只给少量候选打分
_reranker = TextCrossEncoder("BAAI/bge-reranker-v2-m3-int8")   # 智源的多语言重排模型（压缩版，约 570MB）


def rerank(query: str, chunks: list[Chunk], k: int = 2) -> list[tuple[float, Chunk]]:
    scores = list(_reranker.rerank(query, [c.title + "：" + c.text for c in chunks]))
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    return [(float(s), c) for s, c in ranked[:k]]


if __name__ == "__main__":
    from eval_hybrid import CASES, HARD, chunks
    from vector_search import HybridSearcher

    hybrid = HybridSearcher(chunks)
    top1_before = top1_after = 0
    for q, title in CASES + HARD:
        pool = hybrid.search(q, k=5)                    # 第一步：混合检索粗搜 5 段
        after = rerank(q, pool, k=1)[0][1]              # 第二步：重排，取第 1 名
        top1_before += pool[0].title == title
        top1_after += after.title == title
        if pool[0].title != after.title:
            print(f"{q}：重排前第 1 是「{pool[0].title}」，重排后是「{after.title}」（应为「{title}」）")
    n = len(CASES + HARD)
    print(f"第 1 名就是正确答案：重排前 {top1_before}/{n}，重排后 {top1_after}/{n}")
