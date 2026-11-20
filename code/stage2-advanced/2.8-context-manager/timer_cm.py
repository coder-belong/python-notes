import time
from contextlib import contextmanager


@contextmanager
def timer(label: str):
    start = time.perf_counter()     # ① 进入 with 时执行
    try:
        yield                       # ② 暂停在这里，去执行 with 里面的代码
    finally:
        # ③ with 里面的代码执行完（或者出错）后，回到这里执行
        print(f"{label} 用了 {time.perf_counter() - start:.1f}s")


with timer("睡一会"):
    time.sleep(0.5)
# 睡一会 用了 0.5s
