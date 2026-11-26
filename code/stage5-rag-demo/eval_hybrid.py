# eval_hybrid.py：同一组问题（5.5 节的 10 条），比较关键词、向量、混合三种检索的召回
from eval_search import CASES
from load_docs import load_chunks
from search import Searcher
from vector_search import HybridSearcher, VectorSearcher

# 再加 6 条「关键词型」问题：带数字、专有名词，问法和文档的用词一样
HARD = [
    ("12 个月", "积分"),
    ("300 积分", "积分"),
    ("消费满 1000 元", "会员等级"),
    ("7:30", "营业时间"),
    ("超过 30 分钟", "外卖退款"),
    ("Wi-Fi", "自习"),
]

chunks = load_chunks()
methods = {
    "关键词 BM25": lambda q, s=Searcher(chunks): [c for _, c in s.search(q, k=2)],
    "向量": lambda q, s=VectorSearcher(chunks): [c for _, c in s.search(q, k=2)],
    "混合（RRF）": lambda q, s=HybridSearcher(chunks): s.search(q, k=2),
}

if __name__ == "__main__":   # 直接运行才比较；rerank.py import 这里的问题时不执行
    for label, cases in [("口语问题", CASES), ("关键词问题", HARD)]:
        print(f"--- {label}")
        for name, search in methods.items():
            missed = [q for q, title in cases if title not in [c.title for c in search(q)]]
            print(f"{name:<10} {len(cases) - len(missed)}/{len(cases)}   没搜到：{'、'.join(missed) or '无'}")
