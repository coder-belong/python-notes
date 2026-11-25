# chunk_eval.py：切分方式不同，召回率差多少（不调模型，只比检索）
from pathlib import Path

from load_docs import Chunk, read_text, split
from search import Searcher

# 问题 + 正确答案里一定有的一句话（用它判断搜到的段对不对）
CASES = [
    ("积分多久过期？", "12 个月"),
    ("外卖晚了能退款吗", "30 分钟"),
    ("可以带宠物吗", "牵绳"),
    ("营业时间", "7:30"),
    ("饮品不好喝能退吗", "重做"),
    ("储值卡余额能退吗", "转赠"),
    ("店里能自习吗", "插座"),
    ("金卡会员怎么升级", "1000 元"),
    ("会员要收费吗", "不收费"),
    ("有 Wi-Fi 吗", "Wi-Fi"),
]

docs = {p.name: read_text(p) for p in sorted(Path("docs").iterdir())}


def by_heading() -> list[Chunk]:                     # 5.2 节的切法：按小标题
    return [c for name, text in docs.items() for c in split(name, text)]


def whole_file() -> list[Chunk]:                     # 不切：一个文件一段
    return [Chunk(name, "", text.replace("\n", "")) for name, text in docs.items()]


def fixed(size: int, overlap: int = 0) -> list[Chunk]:   # 不管标题，按固定字数切；overlap：相邻两段重叠几个字
    out = []
    for name, text in docs.items():
        body = text.replace("\n", "")
        for i in range(0, len(body), size - overlap):
            out.append(Chunk(name, "", body[i : i + size]))
    return out


def evaluate(chunks: list[Chunk]) -> tuple[int, int]:
    """返回（召回了几条, 平均每个问题放进 prompt 多少字）。"""
    s = Searcher(chunks)
    hit, chars = 0, 0
    for q, ans in CASES:
        found = [c for _, c in s.search(q, k=2)]
        hit += any(ans in c.title + c.text for c in found)
        chars += sum(len(c.text) for c in found)
    return hit, chars // len(CASES)


for name, chunks in [("按小标题", by_heading()), ("整个文件", whole_file()),
                     ("固定 20 字", fixed(20)), ("固定 20 字重叠 8 字", fixed(20, 8)), ("固定 60 字", fixed(60))]:
    hit, chars = evaluate(chunks)
    print(f"{name:<12} {len(chunks):>3} 段   召回 {hit}/{len(CASES)}   每次放进 prompt {chars:>3} 字")
