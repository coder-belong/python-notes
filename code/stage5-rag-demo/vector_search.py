# vector_search.py：向量检索，以及和 BM25 合起来的混合检索
import numpy as np

from embed import embed
from load_docs import Chunk, load_chunks
from search import Searcher


class VectorSearcher:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        vecs = np.array(embed([c.title + "：" + c.text for c in chunks]))   # 建索引：每段算一次向量，存起来
        self.vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)     # 先归一化，之后点积就是余弦相似度

    def search(self, query: str, k: int = 2) -> list[tuple[float, Chunk]]:
        q = np.array(embed([query])[0])
        scores = self.vecs @ (q / np.linalg.norm(q))                       # 问题和每一段的相似度，一次算完
        top = np.argsort(-scores)[:k]                                       # 分数从高到低，取前 k 个的下标
        return [(float(scores[i]), self.chunks[i]) for i in top]


def rrf(*rankings: list[Chunk], k: int = 60) -> list[Chunk]:
    """RRF（倒数排名融合）：每种检索里排第 r 名的，得 1 / (k + r) 分，加起来再排序。
    只看名次不看原始分数，所以 BM25 的分数（几分）和向量的分数（0～1）不用换算就能合并。"""
    score: dict[int, float] = {}
    by_id: dict[int, Chunk] = {}
    for ranking in rankings:
        for r, c in enumerate(ranking, 1):
            score[id(c)] = score.get(id(c), 0) + 1 / (k + r)
            by_id[id(c)] = c
    return [by_id[i] for i in sorted(score, key=score.get, reverse=True)]


class HybridSearcher:
    def __init__(self, chunks: list[Chunk]):
        self.bm25 = Searcher(chunks)
        self.vector = VectorSearcher(chunks)

    def search(self, query: str, k: int = 2, pool: int = 5) -> list[Chunk]:
        a = [c for _, c in self.bm25.search(query, k=pool)]     # 两种检索各取前 pool 个
        b = [c for _, c in self.vector.search(query, k=pool)]
        return rrf(a, b)[:k]


if __name__ == "__main__":
    chunks = load_chunks()
    v = VectorSearcher(chunks)
    for q in ["在店里学习可以吗", "店里有网吗", "我家狗狗能进来吗"]:
        print(q)
        for s, c in v.search(q, k=2):
            print(f"   {s:.2f} {c.source} · {c.title}")
