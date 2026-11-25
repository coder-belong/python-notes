# eval_search.py
from rag import rewrite, searcher

# 问题 + 应该搜到的那一段（小标题）
CASES = [
    ("积分多久过期？", "积分"),
    ("外卖晚了能退款吗", "外卖退款"),
    ("我家狗狗能进来吗", "带宠物"),
    ("几点开门", "营业时间"),
    ("咖啡不好喝能退吗", "饮品退款"),
    ("充的钱能退吗", "储值卡"),
    ("在店里学习可以吗", "自习"),
    ("怎么才能变成金卡", "会员等级"),
    ("办会员要钱吗", "怎么成为会员"),
    ("店里有网吗", "自习"),
]


def recall(use_rewrite: bool) -> None:
    hit = 0
    for q, expected in CASES:
        query = rewrite(q) if use_rewrite else q
        titles = [c.title for _, c in searcher.search(query, k=2)]   # 前 2 段的小标题
        if expected in titles:
            hit += 1
        else:
            print(f"   没搜到：{q}（搜索词：{query}，搜到：{titles}）")
    print(f"{'改写' if use_rewrite else '原句'}：前 2 段里有正确答案 {hit}/{len(CASES)}")


recall(False)
recall(True)
