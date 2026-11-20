def add(a: int, b: int = 0) -> int:     # b 有默认值，可以不传
    """两个数相加。"""                    # 文档字符串：说明函数是干嘛的
    return a + b

print(add(1, 2))        # 3   按位置传
print(add(1))           # 1   b 用默认值
print(add(b=5, a=1))    # 6   按名字传（关键字参数），顺序随意

# ---- 一次返回多个值（其实返回的是元组） ----
def min_max(nums: list[int]) -> tuple[int, int]:
    return min(nums), max(nums)

lo, hi = min_max([3, 1, 2])
print(lo, hi)           # 1 3

# ---- * 后面的参数只能按名字传 ----
def create_user(name: str, *, admin: bool = False) -> str:
    return f"{name} admin={admin}"

print(create_user("Tom", admin=True))   # Tom admin=True
# create_user("Tom", True)              # 报错：admin 必须写成 admin=True

# ---- *args 和 **kwargs ----
def log(*args, **kwargs):
    print(args)      # 多余的位置参数 → 元组
    print(kwargs)    # 多余的关键字参数 → 字典

log(1, 2, level="info")
# (1, 2)
# {'level': 'info'}

def greet(name: str, age: int) -> str:
    return f"{name} {age}"

info = {"name": "Tom", "age": 18}
print(greet(**info))      # Tom 18   ** 把字典拆成关键字参数

# ---- lambda：一行的小函数 ----
double = lambda x: x * 2          # 等价于 def double(x): return x * 2
print(double(3))                  # 6

users = [{"name": "Tom", "age": 20}, {"name": "Amy", "age": 18}]
print(sorted(users, key=lambda u: u["age"]))                # 按年龄从小到大
print(sorted(users, key=lambda u: u["age"], reverse=True))  # 从大到小
print(max(users, key=lambda u: u["age"])["name"])           # Tom   年龄最大的人
print(sorted(["bb", "a", "ccc"], key=len))                  # ['a', 'bb', 'ccc']  key 也可以直接传函数
