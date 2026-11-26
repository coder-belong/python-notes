# similarity.py：意思相近的文字，向量也相近
import numpy as np

from embed import embed

pairs = [
    ("在店里学习可以吗", "店内可以自习"),
    ("店里有网吗", "有插座和免费 Wi-Fi"),
    ("充的钱能退吗", "储值卡余额不能退现金"),
    ("我家狗狗能进来吗", "可以带宠物进店"),
    ("我家狗狗能进来吗", "积分有效期 12 个月"),     # 不相关的一对：对照组
    ("苹果手机多少钱", "苹果多少钱一斤"),           # 字面很像，意思不同
]


def cosine(a: list[float], b: list[float]) -> float:
    """余弦相似度：两个向量方向越接近越接近 1，越不相关越接近 0。"""
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


for x, y in pairs:
    vx, vy = embed([x, y])
    print(f"{cosine(vx, vy):.2f}  {x}  ↔  {y}")
