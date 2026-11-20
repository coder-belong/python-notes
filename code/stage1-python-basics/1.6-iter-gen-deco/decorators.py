import time

def timer(func):                     # 接收原函数
    # 先省掉一行方便看结构；实际写要在这里加 @wraps(func)，见下面的 log_call
    def wrapper(*args, **kwargs):    # 包一层：原样接收所有参数
        start = time.time()
        result = func(*args, **kwargs)   # 调用原函数
        print(f"{func.__name__} 用了 {time.time() - start:.3f} 秒")
        return result
    return wrapper                   # 返回包好的新函数

@timer                               # 等价于 slow_add = timer(slow_add)
def slow_add(a: int, b: int) -> int:
    time.sleep(0.1)
    return a + b

print(slow_add(1, 2))   # 先打印「slow_add 用了 0.10x 秒」，再输出 3

# ---- @wraps：保留原函数的名字 ----
from functools import wraps


def log_call(func):
    @wraps(func)                       # 保留原函数的名字和文档字符串
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}{args}")
        return func(*args, **kwargs)
    return wrapper


@log_call
def add(a: int, b: int) -> int:
    """两个数相加。"""
    return a + b


print(add(1, 2))        # 先打印「调用 add(1, 2)」，再输出 3
print(add.__name__)     # add   不加 @wraps 的话这里是 wrapper
