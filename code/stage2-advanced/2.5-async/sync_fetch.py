import time


def fetch(name: str) -> str:
    time.sleep(1)                       # 模拟等接口返回 1 秒
    return f"{name} 好了"


start = time.perf_counter()
results = [fetch("A"), fetch("B"), fetch("C")]   # 一个等完再等下一个
print(results)                                   # ['A 好了', 'B 好了', 'C 好了']
print(f"用时 {time.perf_counter() - start:.1f}s")  # 用时 3.0s
