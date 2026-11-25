# search.py
import jieba
from rank_bm25 import BM25Okapi

from load_docs import Chunk, load_chunks

jieba.setLogLevel(60)   # 关掉 jieba 加载词典时打印的日志

STOP = {"的", "了", "是", "吗", "呢", "吧", "我", "你", "能", "可以", "怎么", "什么", "多久", "？", "，", "。", "！"}   # 没意义的字词，不参与匹配


def tokenize(text: str) -> list[str]:
    # 中文词之间没有空格，用 jieba 切成词；再去掉停用词。
    # lcut_for_search：长词再拆一遍，「营业时间」切成「营业 时间 营业时间」，搜「营业」也能对上
    return [w for w in jieba.lcut_for_search(text.lower()) if w.strip() and w not in STOP]


class Searcher:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        # 每段的「小标题 + 正文」切成词，建 BM25 索引
        self.bm25 = BM25Okapi([tokenize(c.title + c.text) for c in chunks])

    def search(self, query: str, k: int = 2) -> list[tuple[float, Chunk]]:
        scores = self.bm25.get_scores(tokenize(query))   # 每一段和问题的相关分数
        ranked = sorted(zip(scores, self.chunks), key=lambda x: x[0], reverse=True)   # 按分数从高到低
        return [(s, c) for s, c in ranked[:k] if s > 0]   # 取前 k 段，0 分的不要


if __name__ == "__main__":
    print(tokenize("积分多久过期？"))
    s = Searcher(load_chunks())
    for q in ["积分多久过期？", "外卖晚了能退款吗", "我家狗狗能进来吗"]:
        print(q)
        for score, c in s.search(q):
            print(f"   {score:.2f} {c.source} · {c.title}")
