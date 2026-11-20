# ---- 基本写法 ----
age: int = 18
name: str = "Tom"
price: float = 9.9
ok: bool = True


def greet(name: str, times: int = 1) -> str:   # 参数: 类型，-> 返回值类型
    return name * times


def say(msg: str) -> None:                      # 没有返回值写 None
    print(msg)


# ---- 容器 ----
tags: list[str] = ["a", "b"]
scores: dict[str, int] = {"Tom": 90}            # [键的类型, 值的类型]
point: tuple[int, int] = (1, 2)                 # 固定 2 个
ids: tuple[int, ...] = (1, 2, 3)                # 任意多个 int
unique: set[int] = {1, 2}
rows: list[dict[str, int]] = [{"id": 1}]        # 可以嵌套


# ---- 可能是 None、或者几种类型之一：用 | ----
def find(name: str) -> int | None:    # 找到返回 int，找不到返回 None
    return {"Tom": 1}.get(name)


user_id = find("Amy")
if user_id is not None:               # 先判断，编辑器才知道下面一定是 int
    print(user_id + 1)

value: int | str = 1                  # int 或 str 都行

# ---- 只能是几个固定值：Literal ----
from typing import Literal

Status = Literal["todo", "doing", "done"]   # 类型别名：起个名字，到处复用


def set_status(s: Status) -> None:
    print("状态改成", s)


set_status("done")      # 状态改成 done
set_status("finish")    # 照样能运行（打印「状态改成 finish」），但编辑器会标红：不在这三个值里

# ---- 函数当参数：Callable ----
from collections.abc import Callable


def apply(func: Callable[[int], int], x: int) -> int:   # 接收「参数是一个 int、返回 int」的函数
    return func(x)


print(apply(lambda n: n * 2, 3))     # 6

# ---- 自己写的类也是类型 ----
from dataclasses import dataclass


@dataclass
class User:
    name: str


def names(users: list[User]) -> list[str]:
    return [u.name for u in users]


print(names([User("Tom"), User("Amy")]))   # ['Tom', 'Amy']


# ---- 注解不会在运行时检查 ----
def double(n: int) -> int:
    return n * 2


print(double("ab"))     # abab   标的是 int，传字符串照样运行
