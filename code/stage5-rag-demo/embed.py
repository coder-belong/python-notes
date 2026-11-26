# embed.py：把文字变成向量。换成别的向量模型（比如百炼）只改这个文件
from fastembed import TextEmbedding

MODEL = "BAAI/bge-small-zh-v1.5"   # 智源开源的中文向量模型，小号，CPU 就能跑
DIM = 512                           # 这个模型每段文字变成 512 个数

_model = TextEmbedding(MODEL)       # 第一次运行会从 Hugging Face 下载约 100MB 的模型文件，之后用本机缓存


def embed(texts: list[str]) -> list[list[float]]:
    """一组文字 → 一组向量（每个向量是 DIM 个小数）。"""
    return [v.tolist() for v in _model.embed(texts)]


if __name__ == "__main__":
    import time

    start = time.perf_counter()
    vecs = embed(["积分多久过期？"])
    print(len(vecs[0]), [round(x, 3) for x in vecs[0][:5]], f"{time.perf_counter() - start:.1f}s")
