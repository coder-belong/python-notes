# AI 应用开发笔记

从 Python 基础学起，到用 FastAPI 写后端接口，再到 AI 应用和 Agent 开发。

- **阶段一：Python 语言基础**：只讲常用的写法，不常用的先跳过。
- **阶段二：Python 进阶与工程化**：类型注解、依赖管理、调试、异步、发 HTTP 请求、并发、上下文管理器。
- **阶段三：FastAPI 后端开发**：用 FastAPI + SQLAlchemy 从零做一个 todo 接口项目。
- **阶段四：AI 应用开发**：调大模型、控制成本、结构化输出、函数调用、流式输出。

每节的代码都建议自己敲一遍、跑一遍。代码在 Python 3.12 上跑通过，注释里写的是实际输出。

---

## 准备环境 {#setup}

Mac 自带的 `python3` 版本比较老（3.9），本笔记用 3.12。用 [uv](https://docs.astral.sh/uv/) 管理 Python 版本和依赖：

```bash
mkdir -p ~/study-py && cd ~/study-py
uv venv --python 3.12 .venv      # 在当前目录建虚拟环境，没装 3.12 会自动下载
source .venv/bin/activate        # 激活：提示符前面出现 (.venv)
python --version                 # Python 3.12.x
```

- **虚拟环境**（`.venv` 文件夹）：这个项目专用的 Python 和第三方包，和其他项目互不影响。环境搞坏了就删掉 `.venv` 重建。
- **激活**只对当前终端窗口有效，新开终端要重新 `source`。退出用 `deactivate`。
- 运行一个文件：`python 01_hello.py`。

建一个 `.gitignore`，这些不要提交：

```
.venv/
__pycache__/
*.db
.env
```

**编辑器**：Cursor / VS Code 装 Python 插件和 Ruff 插件，右下角把解释器选成 `.venv` 里的那个。保存时自动格式化，在 `.vscode/settings.json` 里加：

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

---

# 阶段一：Python 语言基础

这个阶段学 Python 本身的语法，只讲写后端常用的写法，不常用的先跳过。

**学完这个阶段，你将会：**

- 用变量、判断、循环、列表、字典处理数据（1.1～1.4）
- 写函数，看懂装饰器：FastAPI 的 `@app.get` 就是装饰器（1.5～1.6）
- 用模块拆分代码，用类和 dataclass 组织数据（1.7～1.10）
- 用 `try / except` 处理错误，读写文件和 JSON（1.11～1.12）

## 1.1 变量、类型、缩进 {#variables}

```python
# 01_basic.py
name = "林必龙"          # str 字符串
age = 18                 # int 整数
price = 9.9              # float 小数
is_ok = True             # bool：True / False，首字母大写
nothing = None           # None：表示「没有值」

print(name, age, price, is_ok, nothing)   # 林必龙 18 9.9 True None
print(type(age))                          # <class 'int'>
```

**类型标注**（可写可不写，写了编辑器能提示、能检查）：

```python
episode: int = 3
title: str = "试拍第一集"
note: str | None = None      # 可以是 str，也可以是 None
```

- 变量的值一眼能看出类型时，一般不写标注；**函数的参数和返回值建议都写**。
- 标注只是提示，Python 运行时不会检查。更多写法集中在第 2.1 节。

**缩进就是语法**：用缩进表示代码块（不用大括号），统一 **4 个空格**。

```python
if age >= 18:
    print("成年")       # 缩进的部分属于 if
print("结束")           # 不缩进，if 结束了
```

**字符串**：单引号、双引号都行，项目里统一一种（Ruff 默认统一成双引号）。

```python
user = "Tom"
n = 3
print(f"{user} 有 {n} 个任务")     # f-string：在字符串里嵌变量，最常用
print(f"{price:.2f}")              # 9.90 保留两位小数
print("a,b,c".split(","))          # ['a', 'b', 'c']
print("  hi  ".strip())            # hi   去首尾空格（打印出来看不到空格了）
print("hello".upper(), "Hello".lower())   # HELLO hello
print("abc".startswith("a"))       # True
```

`split` 的第二个参数是最多切几刀：

```python
full = "林 必 龙"
first, rest = full.split(" ", 1)    # 只切 1 刀 → ['林', '必 龙']
print(first, "|", rest)             # 林 | 必 龙
```

`join` 是 `split` 的反操作，`replace` 替换：

```python
print("-".join(["a", "b", "c"]))       # a-b-c    用 - 把列表拼起来（元素必须是字符串）
print(", ".join(str(n) for n in [1, 2]))   # 1, 2   数字要先转成字符串
print("a.b.c".replace(".", "/"))       # a/b/c
```

**切片 `[开始:结束:步长]`**：取一段，包含开始、不包含结束。字符串、列表都能用。

```python
s = "abcdef"
print(s[1:3])     # bc      下标 1、2
print(s[:2])      # ab      从头开始
print(s[2:])      # cdef    到结尾
print(s[-2:])     # ef      最后两个
print(s[::2])     # ace     每隔一个取
print(s[::-1])    # fedcba  反过来
print(len(s))     # 6       长度
```

**数字**：

```python
print(7 / 2)     # 3.5   除法结果总是小数
print(7 // 2)    # 3     整除
print(7 % 2)     # 1     取余
print(2 ** 10)   # 1024  乘方
print(int("42") + 1, str(42) + "!")   # 43 42!  类型转换
```

## 1.2 判断和循环 {#control-flow}

```python
score = 85
if score >= 90:
    level = "A"
elif score >= 60:          # 注意是 elif
    level = "B"
else:
    level = "C"
print(level)               # B

# 一行版（三元表达式）
status = "及格" if score >= 60 else "不及格"

# 逻辑运算用英文单词
if score > 60 and score < 90:
    print("中等")
if not False:
    print("not 是取反")

# 判断 None 用 is
x = None
if x is None:
    print("x 没有值")
```

**真假值**：`0`、`""`、`[]`、`{}`、`None` 都当作假，其他当作真。

```python
items = []
if not items:              # 空列表算假，not 取反后为真
    print("列表是空的")

if items:                  # 反过来：不为空
    print("列表里有东西")
```

- `if not items:` 等价于 `if len(items) == 0:`，Python 里更习惯前一种。
- **不能写成 `if items is False:`**：`is` 判断的是「是不是同一个东西」，`[]` 和 `False` 不是同一个东西，结果永远是 `False`。用 `==` 也一样，`[] == False` 是 `False`。另外 `false` 小写会直接报 `NameError`。
- `is` 基本只用来和 `None` 比：`if x is None:`、`if x is not None:`。
- 小坑：`0` 也算假。如果 `0` 是一个有意义的值，判断「有没有值」要写 `if count is None:`，不能写 `if not count:`。

**循环**：

```python
for i in range(3):            # 0 1 2
    print(i)

for i in range(1, 10, 2):     # 1 3 5 7 9：起点、终点（不含）、步长
    print(i, end=" ")
print()

n = 0
while n < 3:
    n += 1                    # Python 没有 n++

for i in range(10):
    if i == 2:
        continue              # 跳过这一次
    if i == 4:
        break                 # 结束整个循环
    print(i)                  # 0 1 3
```

## 1.3 列表、字典、元组、集合 {#collections}

**列表 list**：有顺序，可以改。

```python
nums = [3, 1, 2]
nums.append(4)              # 末尾加 → [3, 1, 2, 4]
nums.remove(1)              # 删掉值为 1 的 → [3, 2, 4]
print(nums[0], nums[-1])    # 3 4      -1 是最后一个
print(nums[0:2])            # [3, 2]   切片，含头不含尾
print(len(nums))            # 3
print(sorted(nums))         # [2, 3, 4] 返回新列表
print(2 in nums)            # True
```

**字典 dict**：键值对。

```python
user = {"name": "Tom", "age": 18}
print(user["name"])               # Tom
print(user.get("email"))          # None   键不存在不报错
print(user.get("email", "无"))    # 无     给默认值
user["age"] = 19                  # 改
user["email"] = "t@x.com"         # 加
del user["email"]                 # 删
print("name" in user)             # True   判断键是否存在

for key, value in user.items():   # items() 同时拿到键和值
    print(key, value)
for key in user:                  # 直接遍历拿到的是键
    print(key)
```

**元组 tuple**：和列表像，但不能改。常用来一次返回多个值。

```python
point = (3, 4)
x, y = point          # 拆包：按位置赋值
print(x, y)           # 3 4
a, b = 1, 2
a, b = b, a           # 交换两个变量
```

**拆包**：把列表、元组、字符串这类序列里的值，按位置一次赋给几个变量。不止元组能拆，函数返回多个值、`for` 循环里的 `for k, v in ...` 都是它。

```python
name, age = "Tom,18".split(",")   # split 先得到 ['Tom', '18']，再拆给两个变量
print(name, age)                  # Tom 18   注意 age 是字符串 '18'，要算数得 int(age)

first, *rest = [1, 2, 3, 4]       # 带 * 的接住剩下所有值，得到一个列表
print(first, rest)                # 1 [2, 3, 4]

_, age = ["Tom", 18]              # 用不到的值习惯用 _ 占位
```

左右个数必须一样多，否则直接报错。处理用户输入、文件这种拿不准有几段的数据时要小心：

```python
name, age = "Tom,18,北京".split(",")   # ValueError: too many values to unpack (expected 2)
name, age = "Tom".split(",")           # ValueError: not enough values to unpack (expected 2, got 1)

name, rest = "Tom,18,北京".split(",", 1)   # 只在第一个逗号处切：'Tom'、'18,北京'
```

**集合 set**：不重复。

```python
tags = {"a", "b", "a"}
print(tags)                       # {'a', 'b'}（顺序不固定）
print(set([1, 1, 2]))             # {1, 2}   给列表去重
```

**几个好用的遍历函数**：

```python
names = ["Tom", "Jerry"]
for index, name in enumerate(names):     # 带上序号，注意序号在前
    print(index, name)                    # 0 Tom / 1 Jerry

ages = [18, 20]
for name, age in zip(names, ages):       # 两个列表一一配对
    print(name, age)                      # Tom 18 / Jerry 20
```

**把两个列表组装成数据**：

```python
names = ["Tom", "Jerry"]
ages = [18, 20]

# 名字当键、年龄当值：一个字典
print(dict(zip(names, ages)))            # {'Tom': 18, 'Jerry': 20}

# 每个人一个字典：字典列表（接口返回数据最常用）
users = []
for name, age in zip(names, ages):
    users.append({"name": name, "age": age})
print(users)                             # [{'name': 'Tom', 'age': 18}, {'name': 'Jerry', 'age': 20}]

# 再带上从 1 开始的序号：enumerate 的 start 参数
users = []
for i, name in enumerate(names, start=1):
    users.append({"id": i, "name": name, "age": ages[i - 1]})
print(users[1])                          # {'id': 2, 'name': 'Jerry', 'age': 20}
```

第一种循环可以缩成一行：`users = [{"name": name, "age": age} for name, age in zip(names, ages)]`，这种写法叫推导式，下一节专门讲。

要组装成对象，见第 1.10 节的 dataclass：`[User(name, age) for name, age in zip(names, ages)]`。

## 1.4 推导式：一行生成列表 / 字典 {#comprehensions}

推导式就是「新建空列表 + for 循环 + append」的简写，每组上面是推导式，下面是等价的普通写法：

```python
nums = [1, 2, 3, 4]

# ① 每个数算平方
squares = [n * n for n in nums]                 # [1, 4, 9, 16]

squares = []
for n in nums:
    squares.append(n * n)

# ② 带过滤条件：只要偶数
evens = [n for n in nums if n % 2 == 0]         # [2, 4]

evens = []
for n in nums:
    if n % 2 == 0:
        evens.append(n)

# ③ 从字典列表里取一个字段
rows = [{"id": 1, "name": "Tom"}, {"id": 2, "name": "Jerry"}]
names = [r["name"] for r in rows]               # ['Tom', 'Jerry']

names = []
for r in rows:
    names.append(r["name"])

# ④ 字典推导式：用 {键: 值}
by_id = {r["id"]: r["name"] for r in rows}      # {1: 'Tom', 2: 'Jerry'}

by_id = {}
for r in rows:
    by_id[r["id"]] = r["name"]

print(squares, evens, names, by_id)             # [1, 4, 9, 16] [2, 4] ['Tom', 'Jerry'] {1: 'Tom', 2: 'Jerry'}
```

读法：`[n * n for n in nums]` = 「对 nums 里的每个 n，算出 n * n，放进新列表」。逻辑复杂时还是老老实实写 for 循环。

## 1.5 函数 {#functions}

```python
def add(a: int, b: int = 0) -> int:     # b 有默认值，可以不传
    """两个数相加。"""                    # 文档字符串：说明函数是干嘛的
    return a + b

print(add(1, 2))        # 3   按位置传
print(add(1))           # 1   b 用默认值
print(add(b=5, a=1))    # 6   按名字传（关键字参数），顺序随意
```

**一次返回多个值**（其实返回的是元组）：

```python
def min_max(nums: list[int]) -> tuple[int, int]:
    return min(nums), max(nums)

lo, hi = min_max([3, 1, 2])
print(lo, hi)           # 1 3
```

**`*` 后面的参数只能按名字传**：参数多的时候防止传错位置。

```python
def create_user(name: str, *, admin: bool = False) -> str:
    return f"{name} admin={admin}"

print(create_user("Tom", admin=True))   # Tom admin=True
# create_user("Tom", True)              # 报错：admin 必须写成 admin=True
```

**`*args` 和 `**kwargs`**：接收任意多个参数。

```python
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
```

**`lambda`：一行的小函数**，常用来给 `sorted` / `max` 指定「按什么比」：

```python
double = lambda x: x * 2          # 等价于 def double(x): return x * 2
print(double(3))                  # 6

users = [{"name": "Tom", "age": 20}, {"name": "Amy", "age": 18}]
print(sorted(users, key=lambda u: u["age"]))                # 按年龄从小到大
print(sorted(users, key=lambda u: u["age"], reverse=True))  # 从大到小
print(max(users, key=lambda u: u["age"])["name"])           # Tom   年龄最大的人
print(sorted(["bb", "a", "ccc"], key=len))                  # ['a', 'bb', 'ccc']  key 也可以直接传函数
```

`key` 是一个函数：对每个元素调用一次，按它的返回值来排序。`lambda` 只适合一行能写完的；复杂的老老实实用 `def`。

函数还有一种常见用法是装饰器（`@`），放在下一节和迭代器、生成器一起讲。

## 1.6 迭代器、生成器、装饰器 {#iter-gen-deco}

这三样自己写得不多，但别人的代码里到处都是（FastAPI、pytest、SQLAlchemy 都在用），至少要能看懂。

### 迭代器：for 循环背后在做什么

能放进 `for` 里的叫**可迭代对象**：列表、字符串、字典、文件……`for` 在背后做两件事：先用 `iter()` 拿到一个**迭代器**，再反复调用 `next()` 一个一个取值；取完时迭代器抛出 `StopIteration`，`for` 接住它，循环结束。

```python
nums = [10, 20]
it = iter(nums)        # 从列表拿到迭代器
print(next(it))        # 10
print(next(it))        # 20
# next(it)             # 再取就报 StopIteration：没有了

# for n in nums: print(n) 在背后做的就是上面这些
```

**迭代器只能从头到尾走一遍**，取过的就没了：

```python
it = iter([1, 2, 3])
print(list(it))        # [1, 2, 3]
print(list(it))        # []   已经取完了
```

列表能反复 `for`，是因为每次 `for` 都会重新 `iter()` 出一个新的迭代器。而 `zip()`、`map()`、`enumerate()` 和下面的生成器，返回的本身就是迭代器，用一次就空了：

```python
pairs = zip(["a", "b"], [1, 2])
print(dict(pairs))     # {'a': 1, 'b': 2}
print(dict(pairs))     # {}   第二次就空了；要用多次，先 list(...) 存起来
```

**自己写一个迭代器类**（了解即可，实际用下面的生成器更简单）：实现 `__iter__` 和 `__next__` 两个方法。

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self):            # for 开始时调用：返回迭代器自己
        return self

    def __next__(self) -> int:     # 每取一个值调用一次
        if self.current <= 0:
            raise StopIteration    # 告诉 for：没有了
        self.current -= 1
        return self.current + 1


for n in Countdown(3):
    print(n)                       # 3、2、1，每个一行
```

### 生成器：用 yield 写迭代器

函数里出现 `yield`，调用它不会马上执行，而是得到一个生成器；每次 `for` 取值时跑到下一个 `yield`，交出一个值后暂停。好处是一次只处理一个，不用把所有结果都放进列表。

```python
def read_lines(path: str):
    with open(path, encoding="utf-8") as fp:
        for line in fp:
            yield line.rstrip()       # 交出一行，暂停，等下次再取

from pathlib import Path

Path("a.txt").write_text("第一行\n第二行\n", encoding="utf-8")   # 先准备一个小文件（文件读写见第 1.12 节）

for line in read_lines("a.txt"):      # 一行一行地取，大文件也不占内存
    print(line)                       # 第一行 / 第二行

def count_up(n: int):
    for i in range(n):
        yield i

print(list(count_up(3)))              # [0, 1, 2]   list() 一次取完
```

上面的 `Countdown` 类用生成器写只要三行，`__iter__`、`__next__`、`StopIteration` 都由 Python 自动处理：

```python
def countdown(start: int):
    for n in range(start, 0, -1):
        yield n


print(list(countdown(3)))     # [3, 2, 1]
```

**生成器表达式**：把推导式的 `[]` 换成 `()`，得到的是生成器，不会先把所有结果放进一个列表：

```python
squares = [n * n for n in range(5)]     # 列表：5 个结果全部算好放在内存里
print(squares)                          # [0, 1, 4, 9, 16]

total = sum(n * n for n in range(1_000_000))   # 生成器：边算边加，不建一百万个元素的列表
print(total)                                   # 333332833333500000
```

作为函数唯一的参数时，外面那层括号可以省掉，所以写成 `sum(n * n for n in ...)`。

第 3.9 节的数据库会话、第 3.11 节的 pytest fixture 都用 `yield` 写「先准备 → 交出去用 → 用完收尾」，原理就是这里的「暂停再继续」。

### 装饰器：给函数包一层

函数本身也是一个值，可以当参数传。装饰器就是「接收一个函数，返回包了一层的新函数」，用来给函数加功能而不改它的代码。

```python
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
```

能看懂 `@timer` 就是 `slow_add = timer(slow_add)` 就够了。后面的 `@app.get("/tasks")`、`@dataclass`、`@pytest.fixture` 都是装饰器：自己很少写，主要是会用。

**`@wraps`：保留原函数的名字**。包了一层之后，函数其实变成了 `wrapper`，`__name__`、文档字符串都是 `wrapper` 的。正式写装饰器时给 `wrapper` 加上 `@wraps(func)`，把原函数的这些信息复制过来：

```python
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
```

- **为什么 `timer` 不加也能打印出 `slow_add`**：`wrapper` 里用的是 `func.__name__`，`func` 就是原函数，名字一直是对的。`@wraps` 修的是**外面**看到的那个函数：`slow_add` 这个名字装饰后指向的是 `wrapper`。
- **不加会怎样**：函数照样能调用；但日志、报错栈里显示的是 `wrapper`，`help()` 和编辑器提示看不到参数。最要紧的是 FastAPI 靠读函数签名决定从请求里取哪些参数，不加 `@wraps` 它只能读到 `(*args, **kwargs)`，接口参数会对不上。所以写装饰器一律加上。

**带参数的装饰器**：`@app.get("/tasks")` 多了一对括号，意思是先调用 `app.get("/tasks")`，它返回一个装饰器，再用这个装饰器去包下面的函数。等价于：

```python
# @app.get("/tasks")
# def list_tasks(): ...
#
# 等于：
# list_tasks = app.get("/tasks")(list_tasks)
```

## 1.7 模块和导入 {#modules}

一个 `.py` 文件就是一个**模块**；带 `__init__.py` 的文件夹是一个**包**。

```
study-py/
├── main.py
└── utils/
    ├── __init__.py      # 空文件，表示 utils 是一个包
    └── text.py          # 里面有 def shout(s): ...
```

```python
# main.py
import json                       # 导入整个模块，用的时候写 json.dumps(...)
from pathlib import Path          # 只导入需要的名字
from utils.text import shout      # 从自己的包里导入：包名.文件名
from datetime import datetime as dt   # 起别名
```

- 从**运行命令的目录**开始找模块，所以要在项目根目录运行。
- `datetime` 模块里有个同名的 `datetime` 类：`import datetime` 之后要写 `datetime.datetime.now()`，所以一般写 `from datetime import datetime`。

**只在直接运行时执行的代码**：

```python
def main() -> None:
    print("运行了")

if __name__ == "__main__":   # 被别的文件 import 时不执行
    main()
```

## 1.8 类：属性和方法 {#classes}

```python
class Counter:
    def __init__(self, name: str, start: int = 0) -> None:   # 创建对象时自动调用
        self.name = name          # self 就是「这个对象自己」
        self.count = start

    def add(self, n: int = 1) -> None:    # 方法的第一个参数都是 self
        self.count += n

    def __repr__(self) -> str:            # print 对象时显示什么
        return f"Counter({self.name}={self.count})"


c = Counter("clicks")
c.add()
c.add(5)
print(c.count)     # 6
print(c)           # Counter(clicks=6)
```

**对象不是字典**：类创建出来的是对象，用点号取属性；字典用方括号取值，两种不能混用。

```python
c = Counter("clicks")                  # 对象
d = {"name": "clicks", "count": 0}     # 字典

c.name         # 'clicks'   对象：用点号
d["name"]      # 'clicks'   字典：用方括号
c["name"]      # TypeError: 'Counter' object is not subscriptable
d.name         # AttributeError: 'dict' object has no attribute 'name'

vars(c)        # {'name': 'clicks', 'count': 0}   对象转成字典
```

后面会用到的 dataclass（第 1.10 节）和 pydantic（第 3.3 节）创建出来的也是对象，各有自己转字典的方法：

```python
from dataclasses import asdict, dataclass

from pydantic import BaseModel


@dataclass
class Point:
    x: int
    y: int


p = Point(1, 2)
print(p.x)              # 1                  点号取值
print(asdict(p))        # {'x': 1, 'y': 2}   dataclass 用 asdict() 转字典


class User(BaseModel):
    name: str
    age: int


u = User(name="Tom", age=18)
print(u.name)           # Tom                点号取值
print(u.model_dump())   # {'name': 'Tom', 'age': 18}   pydantic 用 .model_dump() 转字典
```

**类方法 `@classmethod`**：不用先创建对象，直接用类调用。常用来提供「另一种创建对象的方式」。

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @classmethod
    def from_text(cls, text: str) -> "User":    # cls 就是 User 这个类
        name, age = text.split(",")
        return cls(name, int(age))              # 等于 User(name, int(age))


u = User.from_text("Tom,18")
print(u.name, u.age)       # Tom 18
```

继承、多态见第 1.9 节。

## 1.9 继承和多态 {#inheritance}

**继承**：子类自动拥有父类的属性和方法，可以覆盖（重写），也可以加新的。

```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name}: ？"   # 普通动物不知道怎么叫


class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name)     # 先让父类把 name 设好
        self.breed = breed

    def speak(self) -> str:        # 覆盖父类方法
        return f"{self.name}: 汪"


print(Dog("旺财", "柴犬").speak())   # 旺财: 汪
```

- `class Dog(Animal)`：括号里写父类。
- 子类写了自己的 `__init__`，父类的 `__init__` 就**不会自动调用**，要用 `super().__init__(...)` 手动调一次，不然 `self.name` 没设上，后面一用就报 `AttributeError`。
- 子类没写 `__init__`，就直接用父类的。

**多态**：同一个方法名，不同的类各有各的实现；调用的人不用管对象具体是哪个类。

```python
class Cat(Animal):
    def speak(self) -> str:        # 没写 __init__：直接用父类的
        return f"{self.name}: 喵"


# list[Animal]：列表里放的都是 Animal，子类的对象也算
animals: list[Animal] = [Dog("旺财", "柴犬"), Cat("咪咪"), Animal("某某")]
for a in animals:
    print(a.speak())    # 先在对象自己的类里找 speak，找不到再去父类找
# 旺财: 汪
# 咪咪: 喵
# 某某: ？
```

循环里只管调用 `a.speak()`，是汪还是喵由对象自己决定。以后加一种动物，只要再写一个子类，这个循环一行都不用改。

**`isinstance`：判断是不是某个类（或它的子类）的对象**

```python
d = Dog("旺财", "柴犬")
print(isinstance(d, Dog))       # True
print(isinstance(d, Animal))    # True   子类的对象也算父类
print(isinstance(d, Cat))       # False
print(type(d).__name__)         # Dog
```

**抽象基类：规定子类必须实现哪些方法**

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> None: ...   # 只规定要有这个方法，不写实现


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def save(self, key: str, value: str) -> None:
        self.data[key] = value


s = MemoryStorage()
s.save("a", "1")
print(s.data)          # {'a': '1'}
# Storage()            # 报错：抽象类不能直接创建对象
```

子类忘了写 `save`，在创建对象时就会报 `TypeError`，不用等运行到一半才发现。

**鸭子类型：不继承也行**。Python 不检查对象是哪个类，只要有 `speak` 方法，就能放进上面的循环：

```python
class Robot:                   # 没有继承 Animal
    def speak(self) -> str:
        return "哔"


for a in [Dog("旺财", "柴犬"), Robot()]:
    print(a.speak())           # 旺财: 汪 / 哔
```

所以 Python 里继承用得没那么多。入门阶段记住这几条就够了：

- 继承适合「是一种」的关系：狗是一种动物。
- 只是想复用几个函数，不一定要继承：写成普通函数，或者把另一个对象存成属性（组合）更简单。
- 最常见的继承是框架要求的：`class BalanceError(Exception)`（第 1.11 节）、`class TaskCreate(BaseModel)`（pydantic，第 3.3 节）、`class Task(Base)`（SQLAlchemy，第 3.7 节）。

## 1.10 dataclass：只存数据的类 {#dataclass}

只是用来装数据的类，用 `@dataclass` 自动生成 `__init__`、`__repr__`、`__eq__`，不用手写：

```python
from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)   # 列表、字典这种默认值要这样写


t = Task("写笔记")
t.tags.append("学习")
print(t)                           # Task(title='写笔记', done=False, tags=['学习'])
print(t == Task("写笔记", tags=["学习"]))   # True  按字段比较
```

为什么列表默认值不能直接写 `tags: list[str] = []`：那样所有对象会共用同一个列表，dataclass 会直接报错提醒你。`field(default_factory=list)` 表示每次创建对象都新建一个空列表。

**怎么选**：

| 场景 | 用什么 |
|---|---|
| 程序内部传递的数据 | `@dataclass` |
| 接口收到的请求、返回的响应（要校验） | pydantic 的 `BaseModel`（第 3.3 节） |
| 有复杂逻辑的类、异常类 | 普通 class，自己写 `__init__` |

## 1.11 异常 {#exceptions}

```python
def to_int(text: str) -> int | None:
    try:
        return int(text)               # 可能出错的代码放 try 里
    except ValueError as e:            # 出了 ValueError 就到这里，e 是错误对象
        print("转换失败：", e)
        return None
    finally:
        print("不管成功失败都会执行")   # 常用来关文件、释放资源


print(to_int("42"))     # 不管成功失败都会执行 / 42
print(to_int("abc"))    # 转换失败： invalid literal for int() with base 10: 'abc' / 不管成功失败都会执行 / None
```

**常见的错误类型**：

| 错误 | 什么时候出现 |
|---|---|
| `ValueError` | 值不对，比如 `int("abc")` |
| `TypeError` | 类型不对，比如 `"a" + 1` |
| `KeyError` | 字典里没有这个键，比如 `d["x"]` |
| `IndexError` | 列表下标越界 |
| `AttributeError` | 对象没有这个属性或方法 |
| `FileNotFoundError` | 文件不存在 |
| `ZeroDivisionError` | 除以 0 |

**接住不同的错误**：`try` 后面可以跟多个 `except`，每种错误分开处理；几种错误处理方式一样时，用元组写在一个 `except` 里。

```python
def parse(d: dict, key: str) -> int | str:
    try:
        return 100 // int(d[key])
    except KeyError:                               # 字典里没这个键
        return "没有这个键"
    except (ValueError, ZeroDivisionError) as e:   # 元组：这两种都到这里
        return f"值不对：{type(e).__name__}"


data = {"a": "abc", "b": "0", "c": "5"}
print(parse(data, "x"))   # 没有这个键
print(parse(data, "a"))   # 值不对：ValueError          int("abc") 出错
print(parse(data, "b"))   # 值不对：ZeroDivisionError   100 // 0 出错
print(parse(data, "c"))   # 20
```

- **从上往下匹配，只进第一个对上的** `except`，后面的不再看。
- **具体的写前面，宽泛的写后面**。`Exception` 能接住几乎所有错误，放在最前面的话，后面的 `except` 永远轮不到；要兜底就放最后。
- **别一个 `except Exception` 把所有错误都吞掉**：真有 bug 时你不会知道。只接住预料到、知道怎么处理的错误；真要兜底，至少把错误打印出来或记进日志。
- 还有个不常用的 `else`：`try` 里没出错才执行。

```python
text = "42"
try:
    n = int(text)
except ValueError:
    print("不是数字")
else:
    print("转换成功：", n)    # 没出错才走到这里
finally:
    print("一定执行")
# 转换成功： 42
# 一定执行
```

**主动抛错 `raise`**：执行到 `raise`，当前函数立刻停下，后面的代码都不执行（和 `return` 一样）。区别是停下之后去哪里：

- `return`：函数到这里结束，带着结果回到调用它的那一行，**调用方**接着往下执行。
- `raise`：调用方拿不到结果，错误一层层往外抛，找有没有 `try/except` 接住；接住了就跳到 `except` 里继续执行，没人接就整个程序终止并打印报错。`finally` 里的代码不管怎样都会执行。

```python
def check(age: int) -> str:
    print("开始检查")
    if age < 0:
        raise ValueError(f"年龄不能是负数：{age}")
    print("检查通过")              # age < 0 时不会执行
    return "ok"


try:
    check(-1)
    print("这行也不会执行")          # check 里抛了错，try 里剩下的代码跳过
except ValueError as e:
    print("接住了：", e)
print("程序继续往下走")
# 开始检查
# 接住了： 年龄不能是负数：-1
# 程序继续往下走
```

**自定义异常**，按需要从简单到复杂选：

| 情况 | 写法 |
|---|---|
| 只是报个错，给人看文字就行 | 直接用内置的：`raise ValueError("...")` |
| 想和其他错误区分开来 `except` | `class BalanceError(Exception): pass`，然后 `raise BalanceError("余额不足")` |
| 调用方要用到错误里附带的数据 | 自己写 `__init__`，加属性，见下面 |

```python
class BalanceError(Exception):
    def __init__(self, message: str, need: int) -> None:
        super().__init__(message)   # 让 print(e) 显示的是 message
        self.need = need


def pay(balance: int, price: int) -> int:
    if balance < price:
        raise BalanceError("余额不足", need=price - balance)
    return balance - price


try:
    pay(10, 30)
except BalanceError as e:
    print(e, e.need)        # 余额不足 20
```

- `need=price - balance` 是「还差多少钱」：价格 30 − 余额 10 = 20。余额够的时候才会走到最后的 `return balance - price`（付完剩多少）。
- `super().__init__(message)` 不写的话，`print(e)` 会显示 `('余额不足', 20)` 这种元组。
- 什么时候需要 `e.need` 这种属性：比如前端要拿到「还差 20」这个数字，直接跳到充值 20 元的页面，而不是从文字里去解析。

**原则**：知道怎么处理才 `except`；不知道就别接，让它往上抛。千万别写 `except: pass` 把错误悄悄吞掉。

## 1.12 文件和 JSON {#files-json}

`pathlib` 的 `Path` 用来表示「一个文件或文件夹的路径」，建文件夹、读写文件、找文件都通过它；`json` 负责在字典和 JSON 字符串之间转换。下面分五步：建文件夹 → 写 → 读 → 看文件信息 → 找文件。

```python
# demo.py
import json
from pathlib import Path

# ① 准备文件夹和文件路径
folder = Path("data")              # 一个路径对象，指向当前目录下的 data 文件夹（这时还不存在）
folder.mkdir(exist_ok=True)        # 创建文件夹；exist_ok=True：已经有了也不报错
user_file = folder / "user.json"   # 用 / 拼接路径，结果是 data/user.json
print(user_file)                   # data/user.json

# ② 写：字典 → JSON 字符串 → 写进文件
user = {"name": "Tom", "age": 18, "tags": ["学生", "程序员"]}
text = json.dumps(user, ensure_ascii=False, indent=2)   # 转成字符串；中文原样保留，缩进 2 格
user_file.write_text(text, encoding="utf-8")             # 写进文件（文件不存在会自动创建，已存在会覆盖）

# ③ 读：读出文件内容 → JSON 字符串 → 字典
text = user_file.read_text(encoding="utf-8")   # 整个文件读成一个字符串
loaded = json.loads(text)                      # 字符串转回字典
print(loaded["name"], loaded["tags"])          # Tom ['学生', '程序员']

# ④ 看看这个文件的信息
print(user_file.exists())   # True       文件存在吗
print(user_file.name)       # user.json  文件名
print(user_file.stem)       # user       去掉后缀的文件名
print(user_file.suffix)     # .json      后缀

# ⑤ 找出文件夹里所有的 .json 文件
(folder / "config.json").write_text("{}", encoding="utf-8")   # 再建两个文件，方便演示
(folder / "readme.txt").write_text("hi", encoding="utf-8")
for path in sorted(folder.glob("*.json")):   # *.json：所有以 .json 结尾的文件
    print(path)
# data/config.json
# data/user.json              ← readme.txt 不是 .json，没找出来
```

运行完，当前目录下多了这些文件：

```
.
├── demo.py
└── data/
    ├── config.json
    ├── readme.txt
    └── user.json
```

`data/user.json` 的内容（`indent=2` 让它分行缩进，`ensure_ascii=False` 让中文原样写出）：

```json
{
  "name": "Tom",
  "age": 18,
  "tags": [
    "学生",
    "程序员"
  ]
}
```

- 写和读都是两步：**字典 ↔ 字符串** 用 `json`，**字符串 ↔ 文件** 用 `Path`。
- `json.dumps` / `json.loads`：字典 ↔ **字符串**（带 s = string）。`json.dump` / `json.load` 不带 s，直接读写打开的文件，比如 `with open("data/user.json", encoding="utf-8") as fp: user = json.load(fp)`，效果和第 ③ 步一样。
- 不加 `ensure_ascii=False`，中文会写成 `\u5b66\u751f` 这种编码，文件里看不懂。
- `encoding="utf-8"` 每次都写上：不写的话用系统默认编码，Windows 上读写中文可能乱码。
- 路径是**相对于运行命令时所在的目录**，不是 `.py` 文件所在的目录。在别的目录运行 `python 子目录/demo.py`，`data` 会建在你所在的目录。
- JSON 的键必须是字符串；Python 的 `True` / `None` 会转成 `true` / `null`。

大文件不要一次 `read_text()` 全读进内存，按行读：

```python
with open("data/user.json", encoding="utf-8") as fp:   # with 结束时自动关文件
    for line in fp:
        print(line.rstrip())
```

**`with` 是什么**：进入时拿到资源，离开代码块时自动收尾。中途出错也会收尾，不用自己写 `try / finally`。文件、数据库连接、锁都这么用。

```python
with open("a.txt", "w", encoding="utf-8") as fp:
    fp.write("hi")
# 走到这里文件已经关了，等价于：
fp = open("a.txt", "w", encoding="utf-8")
try:
    fp.write("hi")
finally:
    fp.close()
```

---

# 阶段二：Python 进阶与工程化

这个阶段从「会写 Python」到「能写真实项目」，学的是每个项目都会用到的工程能力。

**学完这个阶段，你将会：**

- 给函数标类型，用 uv 管理项目和依赖（2.1～2.2）
- 打日志、读配置、处理时间，看懂报错、打断点调试（2.3～2.4）
- 用 async 同时等好几个请求，用 httpx 调别人的接口，带超时和重试（2.5～2.6）
- 知道进程、线程、协程分别用在哪，用 `with` 管理要关闭的资源（2.7～2.8）

## 2.1 类型注解：给变量和函数标类型 {#type-hints}

前面每节的代码都带着 `name: str`、`-> int` 这样的标注，这一节把常用写法集中讲一遍。

类型注解是写给人和编辑器看的：编辑器能补全、能提前标红，读代码的人一眼知道该传什么。**Python 运行时不检查它**。但后面的 FastAPI、pydantic、SQLAlchemy 都是靠注解干活的，所以一定要会写。

**基本写法**

```python
age: int = 18
name: str = "Tom"
price: float = 9.9
ok: bool = True


def greet(name: str, times: int = 1) -> str:   # 参数: 类型，-> 返回值类型
    return name * times


def say(msg: str) -> None:                      # 没有返回值写 None
    print(msg)
```

**容器**：方括号里写元素的类型。Python 3.9 以后直接用 `list`、`dict`，不用再 `from typing import List`。

```python
tags: list[str] = ["a", "b"]
scores: dict[str, int] = {"Tom": 90}            # [键的类型, 值的类型]
point: tuple[int, int] = (1, 2)                 # 固定 2 个
ids: tuple[int, ...] = (1, 2, 3)                # 任意多个 int
unique: set[int] = {1, 2}
rows: list[dict[str, int]] = [{"id": 1}]        # 可以嵌套
```

**可能是 None、或者几种类型之一：用 `|`**

```python
def find(name: str) -> int | None:    # 找到返回 int，找不到返回 None
    return {"Tom": 1}.get(name)


user_id = find("Amy")
if user_id is not None:               # 先判断，编辑器才知道下面一定是 int
    print(user_id + 1)

value: int | str = 1                  # int 或 str 都行
```

老代码里会看到 `Optional[int]`（等于 `int | None`）和 `Union[int, str]`（等于 `int | str`），意思一样。

**只能是几个固定值：`Literal`**

```python
from typing import Literal

Status = Literal["todo", "doing", "done"]   # 类型别名：起个名字，到处复用


def set_status(s: Status) -> None:
    print("状态改成", s)


set_status("done")      # 状态改成 done
set_status("finish")    # 照样能运行（打印「状态改成 finish」），但编辑器会标红：不在这三个值里
```

**函数当参数：`Callable`**

```python
from collections.abc import Callable


def apply(func: Callable[[int], int], x: int) -> int:   # 接收「参数是一个 int、返回 int」的函数
    return func(x)


print(apply(lambda n: n * 2, 3))     # 6
```

**自己写的类也是类型**

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str


def names(users: list[User]) -> list[str]:
    return [u.name for u in users]


print(names([User("Tom"), User("Amy")]))   # ['Tom', 'Amy']
```

**文件开头的 `from __future__ import annotations`**：让类型标注推迟解析，这样标注里可以用到「后面才定义的类」。加不加对运行结果基本没影响，很多项目习惯每个文件都写；它必须是文件里的第一条代码。

**注解不会在运行时检查**

```python
def double(n: int) -> int:
    return n * 2


print(double("ab"))     # abab   标的是 int，传字符串照样运行
```

- 想在**运行前**发现这类错：编辑器（Pylance）会直接标红；命令行可以用 `mypy` 或 `pyright` 检查整个项目。
- 想在**运行时**真的校验数据（比如接口收到的 JSON）：用 pydantic（第 3.3 节），它按注解检查、转换类型，不对就报错。

**写到什么程度**：函数的参数和返回值都写；变量一眼能看出类型的就不写；一时写不出来的类型先用 `Any`（`from typing import Any`），别卡在类型上。

## 2.2 项目和依赖：uv、pip、pyproject.toml {#tooling}

「准备环境」一节用 `uv venv` 建了虚拟环境、用 `uv pip install` 装包，够做练习。正式项目还要解决两件事：**别人拿到代码，怎么装出一模一样的环境**；**代码风格怎么统一**。

### pip 和 uv

`pip` 是 Python 自带的装包工具；`uv` 是新出的替代品，快很多，还顺带管 Python 版本和虚拟环境。`uv pip ...` 的用法和 `pip ...` 基本一样，两个都要能看懂：

| 做什么 | pip | uv |
|---|---|---|
| 建虚拟环境 | `python -m venv .venv` | `uv venv` |
| 装包 | `pip install httpx` | `uv pip install httpx` |
| 装指定版本 | `pip install "httpx==0.28.1"` | `uv pip install "httpx==0.28.1"` |
| 卸载 | `pip uninstall httpx` | `uv pip uninstall httpx` |
| 看装了哪些 | `pip list` | `uv pip list` |
| 导出依赖清单 | `pip freeze > requirements.txt` | `uv pip freeze > requirements.txt` |
| 按清单安装 | `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |

版本号的写法：`==0.28.1` 只要这个版本；`>=0.28` 这个版本或更新；不写就装最新的。

### 两种记依赖的方式

**requirements.txt**：老办法，一行一个包。`pip freeze` 导出的是当前环境里**所有**包（包括依赖的依赖），分不清哪些是你直接要用的。很多老项目还在用，看到会用就行。

```
fastapi==0.115.0
sqlalchemy==2.0.36
pydantic==2.9.2
...
```

**pyproject.toml + uv.lock**：现在的标准做法。

```bash
uv init --app todo-api        # 新建项目：生成 pyproject.toml 等文件
cd todo-api
uv add fastapi sqlalchemy     # 装包，同时写进 pyproject.toml 的 dependencies
uv add --dev pytest ruff      # 只有开发时用的工具：写进 dev 分组，线上不装
uv remove sqlalchemy          # 卸载，同时从 pyproject.toml 删掉
uv run python main.py         # 用项目的虚拟环境运行，不用先 source 激活
uv sync                       # 别人拿到代码后：按 uv.lock 装出一模一样的环境
```

`uv add` 之后的 `pyproject.toml`（省略了几行 `uv init` 自动生成的）：

```toml
[project]
name = "todo-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [          # 项目直接用到的包：只写你自己 add 的
    "fastapi>=0.115",
    "sqlalchemy>=2.0",
]

[dependency-groups]
dev = [                   # 开发时才用：测试、格式化
    "pytest>=8.0",
    "ruff>=0.6",
]

[tool.ruff]               # 各种工具的配置也写在这个文件里
line-length = 100
```

- `pyproject.toml`：你**直接**要用的包和大致版本范围，手写也行，一般用 `uv add` 维护。
- `uv.lock`：`uv` 自动生成，记着**所有**包（含间接依赖）装的精确版本。不要手改，但**要提交到 git**，这样谁 `uv sync` 装出来的都一样。
- `.venv/` 不提交：别人用 `uv sync` 自己装。

### Ruff：格式化和检查

Ruff 一个工具干两件事：**格式化**（统一缩进、空格、引号、换行）和**检查**（没用到的 import、未定义的变量这类问题）。

```bash
uv run ruff format .          # 把当前目录所有 .py 文件格式化
uv run ruff check .           # 检查问题
uv run ruff check . --fix     # 能自动修的直接修掉
```

格式化前：

```python
import os
def f( x ):
    y=1
    return x
```

`ruff format` 之后：

```python
import os


def f(x):
    y = 1
    return x
```

`ruff check` 对格式化前那段代码的检查结果（ruff 0.17）：

```
a.py:1:1: I001 [*] Import block is un-sorted or un-formatted       import 的排序、空行不规范
a.py:1:8: F401 [*] `os` imported but unused                        os 导入了没用
a.py:3:5: F841 Local variable `y` is assigned to but never used     y 赋了值没用
Found 3 errors.
[*] 2 fixable with `--fix` (1 unsafe fix available with `--fix --unsafe-fixes`).
```

- 带 `[*]` 的 `--fix` 能自动修：这里会删掉 `import os`。
- `F841` 不会自动修：删掉 `y=1` 可能改变程序行为，ruff 让你自己决定。
- 每条开头的 `F401`、`F841` 是规则编号，看不懂就拿编号去搜。

「准备环境」一节已经在编辑器里配了「保存时自动格式化」，平时不用手动跑；提交代码前跑一次 `ruff check` 就行。

## 2.3 日志、环境变量、时间 {#logging-env-time}

```python
import logging
import os
from datetime import UTC, datetime, timedelta

# 程序入口配置一次：INFO 及以上都输出；format 是每行日志的格式（时间 级别 logger 名: 内容）
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)           # 每个文件一个 logger，名字是模块名

log.debug("调试细节")                        # 级别低于 INFO，不输出
log.info("开始处理 %s 条", 3)                # 2026-11-13 14:28:48,622 INFO __main__: 开始处理 3 条
log.warning("快满了")                        # 2026-11-13 14:28:48,622 WARNING __main__: 快满了
log.error("失败了")                          # 2026-11-13 14:28:48,622 ERROR __main__: 失败了

# 环境变量：密码、地址这类配置不写死在代码里
db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg://localhost:5432/todo")   # 读环境变量 DATABASE_URL，没配就用默认值
print(db_url)                               # 没配时：postgresql+psycopg://localhost:5432/todo

# 时间
now = datetime.now(UTC)                     # 带时区的当前时间，存库和返回接口都用 UTC
print(now.isoformat())                      # 2026-11-10T07:00:00.123456+00:00
print(now.strftime("%Y-%m-%d %H:%M:%S"))    # 2026-11-10 07:00:00
print(now - timedelta(days=3))              # 3 天前
```

**为什么用 logging 不用 print**：能分级别（线上只看 warning 以上）、按 `format` 统一带上时间和模块名、可以统一输出到文件或日志系统。

- `__main__` 是 logger 的名字：直接运行的文件，`__name__` 就是 `__main__`；被别的文件导入时是模块名，比如 `app.db`，一看就知道日志是哪个文件打的。
- 不写 `format` 时默认格式是 `INFO:__main__:开始处理 3 条`，没有时间，所以一般都会配上。
- `"开始处理 %s 条", 3`：`%s` 是占位符，后面的 `3` 会填进去。不写成 `f"开始处理 {n} 条"`，是因为这条日志的级别没开时（比如 debug），logging 就不用花时间去拼这个字符串。
- 日志默认输出到**标准错误（stderr）**，`print` 输出到标准输出（stdout）。终端里两个都能看到；用 `python app.py > out.txt` 把输出存进文件时，只有 `print` 的会进文件，日志还会留在终端上。

| 级别 | 用在哪 |
|---|---|
| `debug` | 调试细节，平时不输出 |
| `info` | 正常的关键步骤 |
| `warning` | 不正常但还能继续 |
| `error` | 出错了 |

## 2.4 调试：看懂报错、打断点 {#debugging}

写代码大部分时间不是在写，而是在找「为什么不对」。这一节讲三件事：看懂报错、用 `print` 快速看值、打断点一步一步跑。

### 看懂报错（traceback）

```python
# debug_demo.py
def parse_age(text: str) -> int:
    return int(text)


def load_user(row: dict) -> dict:
    return {"name": row["name"], "age": parse_age(row["age"])}


load_user({"name": "Tom", "age": "十八"})
```

运行 `python debug_demo.py`：

```
Traceback (most recent call last):
  File "debug_demo.py", line 9, in <module>
    load_user({"name": "Tom", "age": "十八"})
  File "debug_demo.py", line 6, in load_user
    return {"name": row["name"], "age": parse_age(row["age"])}
                                        ^^^^^^^^^^^^^^^^^^^^^
  File "debug_demo.py", line 2, in parse_age
    return int(text)
           ^^^^^^^^^
ValueError: invalid literal for int() with base 10: '十八'
```

**从最后一行往上看**：

1. **最后一行**是错误类型和原因：`ValueError`，`int()` 转不了 `'十八'`。大部分时候看这一行就知道怎么回事。
2. **往上一段**是出错的位置：`debug_demo.py` 第 2 行，`parse_age` 函数里，`^^^` 标出了具体是哪段代码。
3. **再往上**是一路调用过来的路径：第 9 行调了 `load_user`，第 6 行调了 `parse_age`。`most recent call last` 的意思就是「越往下越是最后调用的」。

报错里经常夹着很多第三方库的文件路径（比如 `site-packages/fastapi/...`），**先找自己写的文件**，问题一般出在那里。

### print 调试：`f"{x=}"`

最快的办法还是打印。f-string 里在变量后面加个 `=`，会把名字和值一起打出来，不用自己写标签：

```python
x = 3
items = [1, 2]
print(f"{x=}, {items=}, {len(items)=}")   # x=3, items=[1, 2], len(items)=2
```

找完问题记得删掉；要长期保留的输出用 `logging`（第 2.3 节）。

### 断点：程序停下来，一步一步看

在想停下的地方写一行 `breakpoint()`，运行到这里程序会暂停，进入调试器（pdb），可以查看变量、一行一行往下走：

```python
# pdb_demo.py
def total_price(items: list[dict]) -> float:
    total = 0
    for item in items:
        breakpoint()                      # 程序停在这里，进入调试
        total += item["price"] * item["qty"]
    return total


print(total_price([{"price": 9.9, "qty": 2}, {"price": 5, "qty": 1}]))
```

运行 `python pdb_demo.py`，在 `(Pdb)` 后面输入命令：

```
> pdb_demo.py(5)total_price()
-> total += item["price"] * item["qty"]       ← 下一行要执行的代码
(Pdb) p item                                   ← 看变量
{'price': 9.9, 'qty': 2}
(Pdb) p total
0
(Pdb) n                                        ← 执行一行
> pdb_demo.py(3)total_price()
-> for item in items:
(Pdb) p total
19.8
(Pdb) c                                        ← 继续跑，到下一个断点再停
> pdb_demo.py(5)total_price()
-> total += item["price"] * item["qty"]
(Pdb) p item, total
({'price': 5, 'qty': 1}, 19.8)
(Pdb) c
24.8
```

常用命令：

| 命令 | 作用 |
|---|---|
| `p 表达式` | 打印变量或表达式的值，比如 `p item["price"] * 2` |
| `n`（next） | 执行当前这一行，遇到函数调用不进去 |
| `s`（step） | 执行当前这一行，遇到函数调用就进到函数里面 |
| `c`（continue） | 继续运行，直到下一个断点或者程序结束 |
| `l`（list） | 显示当前位置附近的代码 |
| `w`（where） | 显示调用路径：是从哪一路调过来的 |
| `q`（quit） | 直接退出程序（会打印一段 `BdbQuit`，正常） |

### 编辑器里打断点（平时更常用）

Cursor / VS Code 装好 Python 插件后：

1. 在行号左边点一下，出现红点，就是断点（不用改代码写 `breakpoint()`）；
2. 按 F5，选「Python Debugger: Current File」运行；
3. 停下以后，左边能看到所有变量的值，鼠标停在变量上也能看；顶部的按钮对应上面的 `n` / `s` / `c`。

调试 FastAPI 接口：在项目里建 `.vscode/launch.json`，用调试模式启动 uvicorn，然后在接口函数里打断点，用 `/docs` 发请求，程序就会停在断点上：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--port", "8000"]
    }
  ]
}
```

**怎么选**：报错了先看 traceback；想快速看一个值用 `print(f"{x=}")`；逻辑绕、要看很多变量就打断点。

## 2.5 async / await {#async}

后端程序大部分时间都在「等」：等接口返回、等数据库查询、等大模型回答。async 让程序在等一件事的时候，先去做别的事，不用干等。

### 先看效果：一个一个等 vs 一起等

同样是 3 个「要等 1 秒」的任务。普通写法，一个等完再等下一个，一共 3 秒：

```python
import time


def fetch(name: str) -> str:
    time.sleep(1)                       # 模拟等接口返回 1 秒
    return f"{name} 好了"


start = time.perf_counter()
results = [fetch("A"), fetch("B"), fetch("C")]   # 一个等完再等下一个
print(results)                                   # ['A 好了', 'B 好了', 'C 好了']
print(f"用时 {time.perf_counter() - start:.1f}s")  # 用时 3.0s
```

async 写法，3 个一起等，一共 1 秒：

```python
import asyncio
import time


async def fetch(name: str) -> str:      # ① async def：定义异步函数
    await asyncio.sleep(1)              # ② await：在这里等，等的时候让别的任务先跑
    return f"{name} 好了"


async def main() -> None:
    start = time.perf_counter()
    # ③ gather：三个一起开始、一起等，全部完成后按顺序返回结果列表
    results = await asyncio.gather(fetch("A"), fetch("B"), fetch("C"))
    print(results)                                   # ['A 好了', 'B 好了', 'C 好了']
    print(f"用时 {time.perf_counter() - start:.1f}s")  # 用时 1.0s


asyncio.run(main())                     # ④ 程序入口：启动 main，整个程序只写一次
```

### 规则，记住就行

1. 异步函数用 `async def` 定义。
2. 调用异步函数要拿结果，前面必须加 `await`：`result = await fetch("A")`。
3. `await` 只能写在 `async def` 里面。
4. 几件事想一起等，用 `await asyncio.gather(a(), b(), c())`，结果按顺序放在列表里。
5. 程序最外层用 `asyncio.run(main())` 启动，整个程序只写这一次。
6. 异步函数里要等一会儿，用 `await asyncio.sleep(秒)`，不能用 `time.sleep()`，它会卡住所有任务。
7. 写 FastAPI 时不用写 `asyncio.run`，框架会替你启动。

### 常见错误

**忘了写 `await`**：函数不会执行，拿到的不是结果，而是一个「还没执行的协程对象」，还会出警告：

```python
import asyncio


async def fetch(name: str) -> str:
    await asyncio.sleep(1)
    return f"{name} 好了"


async def main() -> None:
    result = fetch("A")                 # 忘了写 await
    print(result)


asyncio.run(main())
# <coroutine object fetch at 0x10a635240>
# RuntimeWarning: coroutine 'fetch' was never awaited
```

**在普通 `def` 里写 `await`**：直接报语法错误，程序跑不起来：

```python
import asyncio


async def fetch(name: str) -> str:
    await asyncio.sleep(1)
    return f"{name} 好了"


def main() -> None:                     # 普通 def，不是 async def
    result = await fetch("A")
# SyntaxError: 'await' outside async function
```

### 设置超时：`asyncio.timeout`

调接口、调大模型都可能卡住，要设一个最长等待时间，超时就不等了：

```python
import asyncio


async def slow() -> str:
    await asyncio.sleep(3)              # 模拟一个要 3 秒的请求
    return "好了"


async def main() -> None:
    try:
        async with asyncio.timeout(1):  # 里面的代码超过 1 秒就取消
            print(await slow())
    except TimeoutError:
        print("超过 1 秒，不等了")


asyncio.run(main())                     # 超过 1 秒，不等了
```

`async with` 是 `with` 的异步版本（第 2.8 节）。超时后会抛出 `TimeoutError`，用 `try / except` 接住。

## 2.6 用 httpx 发 HTTP 请求 {#httpx}

后端也经常要去调别人的接口：第三方服务、内部其他服务，以及阶段四要调的大模型 API。Python 里用 `httpx`（`uv pip install httpx`）。老项目里常见的 `requests` 用法几乎一样，但它不支持 async；FastAPI 测试用的 `TestClient` 底层也是 httpx。

下面的例子用 [httpbin.org](https://httpbin.org)：一个专门给人练习发请求的网站，会把你发过去的东西原样返回。

### GET：查询参数、读 JSON

```python
import httpx

r = httpx.get("https://httpbin.org/get", params={"q": "python", "page": 1}, timeout=10)
print(r.status_code)          # 200
print(r.url)                  # https://httpbin.org/get?q=python&page=1   params 自动拼进网址
data = r.json()               # 响应体按 JSON 解析成 dict，等于 json.loads(r.text)
print(data["args"])           # {'page': '1', 'q': 'python'}
```

httpbin 会把你这次请求的信息整理好原样返回，`data` 是这样一个字典：

```python
{
    "args": {"page": "1", "q": "python"},        # 查询参数，就是上面的 params
    "headers": {                                 # 这次请求带的请求头
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Host": "httpbin.org",
        "User-Agent": "python-httpx/0.28.1",     # httpx 自动带上的
    },
    "method": "GET",
    "origin": "你的公网 IP",
    "url": "https://httpbin.org/get?q=python&page=1",
}
```

`page` 传的是数字 `1`，返回的却是字符串 `"1"`：查询参数拼进网址后都是文本，服务器拿到的只能是字符串。

### POST：发 JSON、带请求头

```python
r = httpx.post(
    "https://httpbin.org/post",
    json={"title": "写笔记", "done": False},        # 自动转成 JSON，并加上 Content-Type
    headers={"Authorization": "Bearer my-token"},  # 带 token 之类的请求头
    timeout=10,
)
print(r.json()["json"])                            # {'done': False, 'title': '写笔记'}
print(r.json()["headers"]["Authorization"])        # Bearer my-token
```

### 状态码不对，httpx 不会自己报错

拿到 404、500 时，`httpx.get` 照样正常返回，要自己检查。最省事的是 `raise_for_status()`：不是 2xx 就抛出 `HTTPStatusError`。

```python
r = httpx.get("https://httpbin.org/status/404", timeout=10)
print(r.status_code)          # 404   不会因为 404 报错

try:
    r.raise_for_status()
except httpx.HTTPStatusError as e:
    print("请求失败：", e.response.status_code)   # 请求失败： 404
```

### 超时

**一定要写 `timeout`**。httpx 默认 5 秒；调大模型这种慢接口要按需要调大，但不能不设，否则对方卡住，你的程序也跟着一直等。

```python
try:
    httpx.get("https://httpbin.org/delay/3", timeout=1)   # 这个地址 3 秒后才返回
except httpx.TimeoutException:
    print("超过 1 秒，超时了")
```

### Client：同一个服务调多次

每次 `httpx.get` 都要重新建连接。同一个服务要调很多次时，建一个 `Client` 复用连接，公共的地址、请求头、超时也只写一次：

```python
with httpx.Client(base_url="https://httpbin.org", headers={"Authorization": "Bearer my-token"}, timeout=10) as client:
    r1 = client.get("/get")                       # 实际请求 https://httpbin.org/get
    r2 = client.post("/post", json={"a": 1})
    print(r1.status_code, r2.status_code)         # 200 200
```

### 异步：AsyncClient + gather 同时发

在 async 代码里（比如 FastAPI 的 `async def` 接口），要用 `AsyncClient`，前面加 `await`。配合第 2.5 节的 `gather`，可以同时发好几个请求：

```python
import asyncio
import time

import httpx


async def main() -> None:
    async with httpx.AsyncClient(base_url="https://httpbin.org", timeout=10) as client:   # 异步版的 Client，用 async with
        start = time.perf_counter()                       # 记下开始时间
        for _ in range(3):                                # 一个一个发：等完一个再发下一个
            await client.get("/delay/1")                  # 这个接口故意等 1 秒才返回
        print(f"一个一个发：{time.perf_counter() - start:.1f}s")

        start = time.perf_counter()
        requests = [client.get("/delay/1") for _ in range(3)]   # 准备 3 个请求；没 await，还没发出去（_ 表示用不到循环变量）
        responses = await asyncio.gather(*requests)       # *requests 拆开传入，等于 gather(请求1, 请求2, 请求3)：一起发、一起等
        print([r.status_code for r in responses])         # 结果顺序和传入顺序一样
        print(f"同时发：{time.perf_counter() - start:.1f}s")


asyncio.run(main())
# 一个一个发：4.5s
# [200, 200, 200]
# 同时发：1.8s
```

`/delay/1` 每个请求都要等 1 秒，再加上网络来回的时间。一个一个发是 3 份时间加起来；同时发是 3 个一起等，总时间接近一个请求的时间。具体秒数看网络，差距是一样的。

在 `async def` 里不要用同步的 `httpx.get`：它等待的时候会卡住整个事件循环，和第 2.5 节说的 `time.sleep` 是一样的问题。

### 失败重试

网络抖动、对方临时出错（5xx）、被限流（429），过一会儿再试往往就好了。但 4xx（参数错、没权限）是请求本身有问题，重试多少次都一样，不该重试。

```python
import time

import httpx


def get_with_retry(url: str, retries: int = 3) -> httpx.Response:
    for attempt in range(1, retries + 1):                 # attempt 依次是 1、2、3，打印「第 1 次」更自然
        try:
            r = httpx.get(url, timeout=5)                 # ① 发请求，最多等 5 秒
            should_retry = r.status_code >= 500 or r.status_code == 429   # ② 5xx、429 值得重试
            if not should_retry:                          # 成功，或 404、401 这类重试也没用的
                return r                                  # 直接返回
            print(f"第 {attempt} 次：{r.status_code}")

        except httpx.TransportError as e:                 # ③ 根本没收到响应：超时、断网、连不上
            print(f"第 {attempt} 次：{type(e).__name__}")   # 打印错误类型，比如 ConnectTimeout

        if attempt < retries:                             # ④ 不是最后一次就等一会儿再试
            time.sleep(2 ** (attempt - 1))                # 等 1、2、4 秒……越等越久（指数退避）

    raise RuntimeError(f"重试 {retries} 次都失败了：{url}")   # ⑤ 每次都失败才会走到这里，放弃并报错

try:
    get_with_retry("https://httpbin.org/status/503")      # 这个地址固定返回 503
except RuntimeError as e:
    print(e)
# 第 1 次：503
# 第 2 次：503
# 第 3 次：503
# 重试 3 次都失败了：https://httpbin.org/status/503
```

- **② 哪些值得重试**：5xx（对方临时出错）、429（被限流）等一会儿可能就好；成功、或者 404、401 这类请求本身有问题的，重试也一样，直接返回。
- **③ 没收到响应也要重试**：超时、断网、连不上都会抛 `httpx.TransportError`。
- **④ 为什么越等越久**：对方已经忙不过来了，大家还马上一起重试只会更糟。
- **⑤ 次数要有上限**：成功的话上面早就 `return` 了，走到最后说明每次都失败，不能无限重试。

实际项目里一般不自己写，而是用现成的库（比如 `tenacity`），或者用 SDK 自带的重试，OpenAI、Anthropic 的 SDK 都自带。这段代码的作用是让你知道它们背后在干什么。

## 2.7 线程、进程、协程和 GIL {#concurrency}

后端要同时处理很多请求，Python 里有三种办法：进程、线程、协程。先搞清楚它们是什么，再记住什么场景用哪个。

### 进程、线程、协程是什么

- **进程**：一个运行起来的程序。你运行 `python app.py` 或者 `uvicorn app.main:app`，系统里就多了一个进程。每个进程有自己的内存，进程之间不共享数据。
- **线程**：进程里真正执行代码的单位。一个进程至少有一个线程（主线程），也可以开多个，同一个进程里的线程共享内存。
- **协程**：就是第 2.5 节的 `async def`。一个线程里可以跑很多个协程，某个协程执行到 `await` 开始等待时，就换另一个协程执行。

拿一个 FastAPI 后端来看，三者是一层套一层的关系：

```
进程：uvicorn 运行的后端程序
└── 线程：主线程
    ├── 协程：请求 A    await 等数据库返回中
    ├── 协程：请求 B    正在执行
    └── 协程：请求 C    await 等大模型返回中
```

一个线程同一时刻只执行一个协程，但大部分时间请求都在等（等数据库、等接口），等的时候让给别的请求，所以一个线程就能同时应付很多请求。

### GIL：Python 的一个限制

GIL 是 Python 里的一把锁，规定**同一个进程里，同一时刻只有一个线程在执行 Python 代码**。结果是：

- **等待为主**（网络请求、读写数据库、读写文件）：多线程、协程都有用，等待的时间可以叠在一起。
- **计算为主**（大循环、处理图片、数据分析）：多线程没用，开再多线程也是轮流算。要用**多进程**，每个进程有自己的 GIL，才能用上多个 CPU 核。

写后端、调大模型几乎都是在「等」，所以 GIL 平时影响不大。

### 怎么选

| 场景 | 用什么 |
|---|---|
| 写 FastAPI 接口、调接口、调大模型 | `async def` + `await`（第 2.5 节） |
| FastAPI 接口里用的库只有同步版本 | 普通 `def`，FastAPI 会自动放到线程里跑 |
| async 代码里要调用一个同步的慢函数 | `await asyncio.to_thread(函数, 参数)`，见下面的例子 |
| 大量计算 | 多进程（`concurrent.futures` 的 `ProcessPoolExecutor`，用到再查） |
| 很重、很慢的后台任务（比如生成视频） | 交给任务队列，接口立刻返回（阶段六） |

### 例子：async 里调用同步的慢函数

有些库只有同步版本，直接在 `async def` 里调用，等待期间整个线程都被卡住，别的请求也没法处理。用 `asyncio.to_thread` 把它放到另一个线程里跑：

```python
import asyncio
import time


def slow_sync(name: str) -> str:    # 一个只有同步版本的慢函数
    time.sleep(1)
    return f"{name} 完成"


async def main() -> None:
    start = time.perf_counter()
    # 两个慢函数分别放到两个线程里跑，await 等结果；等的时候不会卡住其他协程
    results = await asyncio.gather(
        asyncio.to_thread(slow_sync, "A"),
        asyncio.to_thread(slow_sync, "B"),
    )
    print(results)                                     # ['A 完成', 'B 完成']
    print(f"用时 {time.perf_counter() - start:.1f}s")    # 用时 1.0s，两个一起等，不是 2 秒


asyncio.run(main())
```

## 2.8 with 和上下文管理器 {#context-manager}

有些东西用之前要打开，用完一定要关闭：文件、网络连接、数据库会话。`with` 的作用是**离开代码块时自动关闭**，不管是正常执行完还是中途出错。

### with 怎么用

```python
# with 写法：离开 with 时自动关闭文件
with open("a.txt", "w", encoding="utf-8") as f:   # f 就是打开的文件
    f.write("hi")
# 走到这里，文件已经关了

# 不用 with 的等价写法：要自己用 try / finally 保证一定关闭
f = open("a.txt", "w", encoding="utf-8")
try:
    f.write("hi")
finally:
    f.close()            # 中途出错也会执行
```

能放在 `with` 后面的对象叫**上下文管理器**。后面会经常见到这些：

| 写法 | 离开时自动做什么 |
|---|---|
| `with open(...) as f:` | 关闭文件（第 1.12 节） |
| `with httpx.Client() as client:` | 关闭网络连接（第 2.6 节） |
| `async with httpx.AsyncClient() as client:` | 同上，异步版本 |
| `async with asyncio.timeout(1):` | 超时就取消里面的代码（第 2.5 节） |
| `with SessionLocal() as session:` | 关闭数据库会话（第 3.8 节） |

**规则，记住就行**：

1. 用完要关闭、要释放的东西，用 `with` 打开。
2. `as` 后面的变量，就是打开后拿到的东西。
3. 离开 `with` 时自动收尾，出错了也会。
4. 异步的写 `async with`，只能写在 `async def` 里。
5. 一次打开多个，用逗号隔开：`with open("a.txt") as src, open("b.txt", "w") as dst:`。

### 自己写一个：@contextmanager

写一个带 `yield` 的函数，加上 `@contextmanager`：`yield` 前面是进入 `with` 时做的事，后面是离开时做的事。

```python
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
```

`yield` 外面要包 `try / finally`，否则 `with` 里面出错时，第 ③ 步会被跳过。

### FastAPI 里会见到的

FastAPI 的 `lifespan` 就是一个异步的上下文管理器：`yield` 前是服务启动时做的事，`yield` 后是服务关闭时做的事。

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("启动：建表、建连接池")       # 服务启动时执行一次
    yield                                # 服务运行中
    print("关闭：释放连接池")           # 服务停止时执行一次


app = FastAPI(lifespan=lifespan)
```

第 3.9 节依赖注入里带 `yield` 的 `get_session` 也是一样：`yield` 前开数据库会话，`yield` 后关闭，FastAPI 在每个请求前后替你执行。

---

# 阶段三：FastAPI 后端开发

这个阶段从零做一个 todo 后端：先在本地把接口跑通，再一步步升级成能上线、多人使用的后端。

**学完这个阶段，你将会：**

- 用 FastAPI 写接口，统一返回格式和错误处理（3.1～3.5）
- 手写 SQL，再用 SQLAlchemy 在接口里增删改查（3.6～3.10）
- 给接口写自动化测试，按业务拆分文件（3.11～3.12）
- 做注册登录，让每个人只能看到自己的数据（3.13～3.14）
- 用 Alembic 管理表结构的变化，把后端部署上线（3.15～3.16）

## 3.1 项目准备 {#project-setup}

```bash
mkdir -p todo-api/app todo-api/tests && cd todo-api
touch app/__init__.py tests/__init__.py
uv pip install fastapi "uvicorn[standard]" sqlalchemy "psycopg[binary]" pytest httpx python-dotenv
```

- `__init__.py`：空文件，标记 `app`、`tests` 是包，这样就能写 `from app.db import ...`。严格说 Python 3.3 以后没有它也能 import，但 pytest 这类工具在有它时更稳定，项目里习惯都放。
- 已经在上一级激活过 `.venv` 就不用再建虚拟环境，包装进同一个 `.venv` 就行。

| 包 | 作用 |
|---|---|
| fastapi | 写接口的框架 |
| uvicorn | 运行接口的服务器 |
| sqlalchemy | 用 Python 类操作数据库 |
| psycopg | Python 连 Postgres 的驱动，SQLAlchemy 通过它发 SQL（第 3.7 节） |
| pytest | 跑测试 |
| httpx | 测试里的 `TestClient` 要用它 |
| python-dotenv | 启动时读取 `.env` 文件里的配置（第 3.7 节） |

`"uvicorn[standard]"`、`"psycopg[binary]"` 要加引号，否则 zsh 会把方括号当通配符。`[binary]` 表示装编译好的版本，不用自己装 Postgres 的开发库。

最后的目录结构：

```
todo-api/
├── app/
│   ├── __init__.py
│   ├── db.py          # 连数据库、会话
│   ├── models.py      # 表定义
│   ├── schemas.py     # 请求 / 响应的数据格式
│   ├── response.py    # 统一响应格式：success
│   ├── errors.py      # 错误处理：fail 和异常处理器
│   └── main.py        # 接口
└── tests/
    ├── __init__.py
    └── test_tasks.py
```

## 3.2 第一个接口 {#first-api}

下面是一组 RESTful 风格的接口示例：同一个资源 `/users`，用不同的 HTTP 方法表示查、增、改、删。分几块写进同一个文件 `app/hello.py`。

**准备：建 app、定义请求体**

```python
# app/hello.py
from typing import Annotated

from fastapi import FastAPI, Header             # Header：从请求头取参数（最后一块用）
from pydantic import BaseModel                  # 定义请求体的格式（下一节细讲）

app = FastAPI()                                 # 创建应用，下面的接口都挂在它上面


class User(BaseModel):                          # 请求体格式：{"name": "Tom", "age": 18}
    name: str                                   # 必填，字符串
    age: int                                    # 必填，整数
```

**查：列表和详情**

```python
# app/hello.py（接着写）
@app.get("/users")                              # 列表：GET /users?q=tom&page=2
def list_users(q: str | None = None, page: int = 1) -> dict:   # 普通参数 = 查询参数；有默认值，不传也行
    return {"q": q, "page": page}               # 访问 /users 返回 {"q": null, "page": 1}


@app.get("/users/{user_id}")                    # 详情：GET /users/5
def get_user(user_id: int) -> dict:             # 名字和路径里的 {user_id} 一样 = 路径参数，自动转成 int
    return {"user_id": user_id}                 # {"user_id": 5}
```

**增：请求体**

```python
# app/hello.py（接着写）
@app.post("/users", status_code=201)            # 新建：成功返回 201 Created，不写默认是 200
def create_user(body: User) -> User:            # 类型是 BaseModel 子类 = 从 JSON 请求体读
    return body                                 # 直接返回 pydantic 对象，FastAPI 转成 JSON：{"name": "Tom", "age": 18}
```

**改：路径参数 + 请求体**

```python
# app/hello.py（接着写）
@app.put("/users/{user_id}")                    # 修改：PUT /users/5，请求体 {"name": "Tom", "age": 18}
def update_user(user_id: int, body: User) -> dict:   # 两种参数可以一起用
    return {"user_id": user_id, "updated": body}     # 字典里套 pydantic 对象也行：{"user_id": 5, "updated": {"name": "Tom", "age": 18}}
```

**删：路径参数**

```python
# app/hello.py（接着写）
@app.delete("/users/{user_id}")                 # 删除：DELETE /users/5
def delete_user(user_id: int) -> dict:
    return {"deleted": user_id}                 # {"deleted": 5}
```

**请求头：Header()**

```python
# app/hello.py（接着写）
@app.get("/me")                                 # GET /me，带请求头 X-Token: abc
def me(x_token: Annotated[str, Header()]) -> dict:   # 类型是 str，Header() 说明从请求头取；没带就返回 422
    return {"token": x_token}                   # {"token": "abc"}
```

- **`Annotated[类型, 说明]`**：`x_token` 的类型是 `str`，`Header()` 说明它从「请求头」里取。
- **参数名怎么对应请求头**：`x_token` 自动对应 `X-Token`，下划线换成横线，不分大小写。

在 `todo-api/` 目录启动，然后打开 http://127.0.0.1:8000/docs 点着试（Try it out → Execute）：

```bash
uvicorn app.hello:app --reload
```

**参数从哪里来**，看函数参数怎么写：

| 写法 | 来源 | 例子 |
|---|---|---|
| 名字在路径 `{...}` 里 | 路径参数 | `/users/5` |
| 普通类型（str、int…） | 查询参数 | `/users?q=tom&page=2` |
| 类型是 `BaseModel` 子类 | JSON 请求体 | `{"name": "Tom", "age": 18}` |
| `Annotated[str, Header()]` | 请求头 | `X-Token: abc` |

- **有默认值是可选，没默认值是必填**：`list_users` 的 `q`、`page` 都有默认值，直接访问 `/users` 也行，`q` 是 `None`、`page` 是 1；`get_user` 的 `user_id` 没默认值，必须传。
- **必填的没传、或者类型不对，自动返回 422**，函数根本不会执行：

  | 请求 | 为什么 422 |
  |---|---|
  | `GET /users/abc` | `user_id` 要 int，`abc` 不是数字 |
  | `GET /users?page=abc` | `page` 要 int |
  | `POST /users`，请求体只有 `{"name": "Tom"}` | `User` 里的 `age` 是必填，没传 |

- RESTful：路径用名词复数表示资源，动作用 HTTP 方法表示，不写 `/getUser`、`/users/list` 这种。

## 3.3 请求体和响应：pydantic {#pydantic}

接口收到的数据（请求体）和返回的数据（响应体），一般都会先用 pydantic 定义好「长什么样」：有哪些字段、什么类型、哪些必填、有什么限制。上一节的 `User` 就是一个最简单的例子。这样做的好处：

- 前端传错了，FastAPI 自动返回 422，不用自己一个个写 `if` 判断；
- 返回给前端的字段是固定的，不会把密码这类字段不小心带出去；
- `/docs` 里自动生成接口文档，前端照着对接。

这些模型一般统一放在 `schemas.py` 里，按用途起名：`TaskCreate` 是新建时的请求体，`TaskOut` 是返回给前端的响应体。

继承 `BaseModel`，写好字段和类型，pydantic 会自动生成 `__init__`，并做**校验和类型转换**：

```python
# app/schemas.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """新建任务的请求体。"""
    title: str = Field(min_length=1, max_length=200)   # Field 加校验规则
    note: str | None = None                            # 可以不传


class TaskOut(BaseModel):
    """返回给前端的一条任务。"""
    model_config = ConfigDict(from_attributes=True)   # 允许直接从对象创建，见本节末尾的补充

    id: int
    title: str
    done: bool
    note: str | None          # 没有默认值：必须给，但可以是 None
    created_at: datetime      # 输出 JSON 时自动转成 ISO 字符串
    updated_at: datetime
```

**请求体：校验前端传来的数据**

接口参数的类型写成 `TaskCreate`，FastAPI 就会从请求体读 JSON，按 `TaskCreate` 校验。校验通过才执行函数，`body` 拿到的是一个 `TaskCreate` 对象；不通过就直接返回 422，函数根本不会执行：

```python
@app.post("/tasks")
def create_task(body: TaskCreate) -> dict:
    print(body)                  # title='写笔记' note=None      是 TaskCreate 对象，不是字典
    print(body.title, body.note) # 写笔记 None                  用点号取值
    print(body.model_dump())     # {'title': '写笔记', 'note': None}   要字典就调 model_dump()
    return {"title": body.title}


# ✅ 请求体 {"title": "写笔记"}
#    → 200 {"title": "写笔记"}

# ❌ 请求体 {"title": ""}：title 至少 1 个字符
#    → 422 {"detail": [{"type": "string_too_short", "loc": ["body", "title"], "msg": "String should have at least 1 character", ...}]}

# ❌ 请求体 {"note": "x"}：没传必填的 title
#    → 422 {"detail": [{"type": "missing", "loc": ["body", "title"], "msg": "Field required", ...}]}

# ❌ 请求体 {"title": 123}：title 要字符串，传了数字
#    → 422 {"detail": [{"type": "string_type", "loc": ["body", "title"], "msg": "Input should be a valid string", ...}]}
```

`loc` 说明是哪里出了错：`["body", "title"]` 就是请求体里的 `title`。下一节会把这种默认格式改成项目统一的 `{code, msg, data}`。

**响应体：只返回模型里定义的字段**

接口的返回类型写成 pydantic 模型，FastAPI 会按模型过滤一遍，模型里没有的字段不会返回给前端。直接返回 dict 就没有这一步：

```python
class UserOut(BaseModel):
    id: int
    username: str


row = {"id": 1, "username": "tom", "password_hash": "$argon2id$..."}   # 从数据库查出来的一行


@app.get("/a")
def a() -> dict:                # 返回 dict：数据里有什么就返回什么
    return row
# 前端收到：{"id":1,"username":"tom","password_hash":"$argon2id$..."}   密码哈希也带出去了


@app.get("/b")
def b() -> UserOut:             # 返回类型写成 UserOut：按模型过滤
    return row                  # 返回的还是同一个 row
# 前端收到：{"id":1,"username":"tom"}                                  password_hash 被去掉了
```

所以请求体用 pydantic **校验**前端传来的数据，响应体用 pydantic **规定和过滤**返回给前端的数据。

**pydantic 字段的常用写法**：上面 `TaskCreate`、`TaskOut` 里的字段只写了类型，还可以给字段加更多限制。下面这个 `TaskFilter` 是一个「查任务列表时的筛选条件」模型，演示几种常见的字段写法：

```python
from typing import Literal

class TaskFilter(BaseModel):
    status: Literal["todo", "doing", "done"]          # 只能是这几个值之一
    page: int = Field(1, ge=1)                        # 默认 1，最小 1
    size: int = Field(20, ge=1, le=100, description="每页条数")   # description 显示在 /docs 里
```

| `Field` 参数 | 作用 |
|---|---|
| 第一个位置参数 | 默认值（不写就是必填） |
| `min_length` / `max_length` | 字符串长度 |
| `ge` / `le` | 数字 大于等于 / 小于等于 |
| `description` | 文档里的说明 |

### 补充：`from_attributes=True`，从对象直接转成 `TaskOut`

上面 `TaskOut` 里写的 `model_config = ConfigDict(from_attributes=True)`，作用是可以从一个对象直接创建 `TaskOut`：

```python
from datetime import datetime


class Task:                          # 假装是从数据库查出来的一条任务（第 3.7 节会讲真的）
    def __init__(self) -> None:
        self.id = 1
        self.title = "写笔记"
        self.done = False
        self.note = None
        self.created_at = datetime(2026, 11, 14, 10, 0)
        self.updated_at = datetime(2026, 11, 14, 10, 0)
        self.user_id = 7             # TaskOut 里没有这个字段，转换时会被丢掉


task = Task()

# 不用 from_attributes：一个个字段手写
out = TaskOut(id=task.id, title=task.title, done=task.done, note=task.note,
              created_at=task.created_at, updated_at=task.updated_at)

# 用 from_attributes：按 TaskOut 的字段名，自动去 task 上读同名属性
out = TaskOut.model_validate(task)
print(out)
# id=1 title='写笔记' done=False note=None created_at=datetime.datetime(2026, 11, 14, 10, 0) updated_at=...
# 两种写法结果完全一样；user_id 不在 TaskOut 里，不会返回给前端

# 没加 from_attributes=True 的模型，传对象进去会报错：
# ValidationError: Input should be a valid dictionary or instance of TaskOut
```

第 3.10 节就是用 `TaskOut.model_validate(task)` 把数据库里查出来的任务转成返回给前端的格式。

## 3.4 统一响应格式：success {#errors}

前端调每个接口，都要判断成功还是失败、取出数据、失败时弹出提示。如果每个接口返回的格式都不一样，前端就得一个个特殊处理。所以项目里一般会约定一个**统一的响应格式**，所有接口都按它返回。

这一节先定好格式，再写一个 `success()` 函数，成功时用它包装数据。失败怎么返回，下一节讲。

**约定**：HTTP 状态码照实返回；响应体统一是 `{code, msg, data}`。

| 情况 | HTTP 状态码 | 响应体 |
|---|---|---|
| 成功 | 200、201 | `{"code": 200, "msg": "ok", "data": 数据}` |
| 失败 | 404、409…… | `{"code": -1, "msg": "提示文字", "data": null}`（下一节） |

```python
# app/response.py
from __future__ import annotations


def success(data: object = None, msg: str = "ok") -> dict:
    """成功时把数据包一层：{"code": 200, "msg": msg, "data": data}"""
    return {"code": 200, "msg": msg, "data": data}


# success({"id": 1})          → {"code": 200, "msg": "ok", "data": {"id": 1}}
# success(msg="删除成功")      → {"code": 200, "msg": "删除成功", "data": None}
```

**动手试**（不连数据库）：

```python
# api_demo.py（放在 todo-api/ 下）
from fastapi import FastAPI

from app.response import success

app = FastAPI()

TASKS = {1: "写笔记"}          # 先用 dict 假装数据库


@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    return success({"id": task_id, "title": TASKS[task_id]})


@app.post("/tasks", status_code=201)    # 新建成功返回 201，不写默认是 200
def create_task(title: str) -> dict:
    new_id = max(TASKS) + 1
    TASKS[new_id] = title
    return success({"id": new_id, "title": title}, msg="创建成功")
```

`uvicorn api_demo:app --reload` 启动，实际结果：

| 请求 | HTTP | 响应体 |
|---|---|---|
| `GET /tasks/1` | 200 | `{"code": 200, "msg": "ok", "data": {"id": 1, "title": "写笔记"}}` |
| `POST /tasks?title=读书` | 201 | `{"code": 200, "msg": "创建成功", "data": {"id": 2, "title": "读书"}}` |

现在查一个不存在的任务，比如 `GET /tasks/99`，`TASKS[99]` 会报 `KeyError`，前端收到 500 和一段纯文本，不是约定的格式。下一节处理这个问题。

## 3.5 错误处理 {#error-handling}

接口出错时，也要按上一节的约定返回 `{"code": -1, "msg": "提示文字", "data": null}`。错误分两种：

- **业务错误**：任务不存在、名字重复……由你在接口里主动抛出；
- **不是你抛的错误**：前端传的参数不对、访问了不存在的接口、代码里有 bug，这些是 FastAPI 自己发现的。

这一节先处理业务错误，再把第二种也拦截下来，最后附一张常用状态码表。

### 业务错误：fail

接口里只有一条规矩：**成功就 `return success(...)`，失败就 `raise fail(...)`**。

```python
# app/errors.py（新建）
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status: int, msg: str) -> None:
        super().__init__(msg)    # 打印这个异常时显示 msg
        self.status = status     # HTTP 状态码：404、409……
        self.msg = msg           # 给用户看的提示


# 1. 失败：raise fail(状态码, 提示)
def fail(status: int, msg: str) -> ApiError:
    return ApiError(status, msg)


# 常用的错误写成函数，各处直接 raise task_not_found()
def task_not_found() -> ApiError:
    return fail(404, "没有这个任务")


# 2. 统一的错误处理器：任何接口抛出 ApiError，都由这里转成 JSON 响应
#    install(app) 在启动时调用一次，只负责登记；之后每次有接口 raise fail(...)，
#    FastAPI 都会自动调用 handle_api_error，接口里不用自己处理
def install(app: FastAPI) -> None:
    @app.exception_handler(ApiError)              # 登记：只处理 ApiError 这一种异常
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        # exc 就是接口里 raise 出来的那个异常对象
        return JSONResponse(
            status_code=exc.status,               # HTTP 状态码：raise fail(404, ...) 里的 404
            content={"code": -1, "msg": exc.msg, "data": None},   # 响应体：msg 是 fail 的第二个参数
        )
```

**出错时代码怎么走**（以 `GET /tasks/99` 为例）：

1. 接口里执行 `raise task_not_found()`，函数立即中断。
2. 异常往外抛，被 FastAPI 接住。
3. FastAPI 发现是 `ApiError`，调用启动时登记的 `handle_api_error`。
4. 返回 404 和 `{"code": -1, "msg": "没有这个任务", "data": null}`。

把上一节的 `api_demo.py` 改成这样，分三块写进同一个文件：

**准备：建 app、登记错误处理器**

```python
# api_demo.py
from fastapi import FastAPI

from app import errors
from app.errors import fail, task_not_found      # 业务错误：上面 errors.py 里定义的
from app.response import success                 # 成功的统一格式（第 3.4 节）

app = FastAPI()
errors.install(app)            # 创建 app 之后调用一次：登记错误处理器（正式项目写在 main.py 里）

TASKS = {1: "写笔记"}          # 先用字典假装数据库：id → 标题
```

**查一条：不存在就 404**

```python
# api_demo.py（接着写）
@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    if task_id not in TASKS:                     # 字典里没有这个 id
        raise task_not_found()                   # 抛 404，函数到这里就结束了
    return success({"id": task_id, "title": TASKS[task_id]})   # 有就正常返回
```

**新建：重名就 409**

```python
# api_demo.py（接着写）
@app.post("/tasks", status_code=201)
def create_task(title: str) -> dict:
    if title in TASKS.values():                  # 已经有同样的标题
        raise fail(409, "已经有同名任务了")        # 抛 409，后面不会执行
    new_id = max(TASKS) + 1                      # 现有最大 id + 1 当新 id
    TASKS[new_id] = title                        # 存进字典
    return success({"id": new_id, "title": title}, msg="创建成功")
```

实际结果：

| 请求 | HTTP | 响应体 |
|---|---|---|
| `GET /tasks/1` | 200 | `{"code": 200, "msg": "ok", "data": {"id": 1, "title": "写笔记"}}` |
| `GET /tasks/99` | 404 | `{"code": -1, "msg": "没有这个任务", "data": null}` |
| `POST /tasks?title=写笔记` | 409 | `{"code": -1, "msg": "已经有同名任务了", "data": null}` |
| `POST /tasks?title=读书` | 201 | `{"code": 200, "msg": "创建成功", "data": {"id": 2, "title": "读书"}}` |

**两个要点**：

```python
# ① 失败时固定写 raise fail(...)。fail() 只是生成一个错误，前面不写 raise 就什么都不会发生
def check() -> str:
    fail(409, "已经有同名任务了")        # 忘了写 raise
    return "继续往下走了"

print(check())                          # 继续往下走了      错误没抛出去，函数照常执行完


# ② 一定要调用 errors.install(app)。不调用的话，FastAPI 不认识 fail 抛出的错误，会当成代码 bug
app = FastAPI()                         # 没有 errors.install(app)
# GET /tasks/99 → 500 Internal Server Error（纯文本，不是约定的格式）
# 调用了 install → 404 {"code": -1, "msg": "没有这个任务", "data": null}
```

### 不是你抛的错误：全部拦截

上面的 `install()` 只拦截了 `ApiError`。参数不对、接口不存在、代码 bug 这些错误是 FastAPI 自己发现的，不会经过 `handle_api_error`，默认返回的是：

| 情况 | 默认返回 |
|---|---|
| 参数校验失败（缺字段、类型不对） | 422 `{"detail": [{"type": ..., "loc": [...], "msg": ...}]}` |
| 路径不存在、请求方法不对 | 404 `{"detail": "Not Found"}` / 405 `{"detail": "Method Not Allowed"}` |
| 代码 bug | 500 纯文本 `Internal Server Error`，不是 JSON |

在 `install()` 里把这几种错误也拦截下来。把 `app/errors.py` 换成下面的完整版，分五块写进同一个文件。

**开头：导入、业务错误、统一的错误格式**

```python
# app/errors.py（完整版）
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError      # ② 参数校验失败时 FastAPI 抛的异常
from fastapi.responses import JSONResponse                 # 自己决定状态码和响应体
from starlette.exceptions import HTTPException as StarletteHTTPException   # ③ 404 / 405 时框架抛的异常


class ApiError(Exception):                      # 业务错误，和上面新建的版本一样
    def __init__(self, status: int, msg: str) -> None:
        super().__init__(msg)                   # 打印这个异常时显示 msg
        self.status = status                    # HTTP 状态码：404、409……
        self.msg = msg                          # 给用户看的提示


def fail(status: int, msg: str) -> ApiError:    # 接口里 raise fail(状态码, 提示)
    return ApiError(status, msg)


def task_not_found() -> ApiError:               # 常用的错误写成函数
    return fail(404, "没有这个任务")


def error_response(status: int, msg: str) -> JSONResponse:
    """所有错误都用这一个格式返回。"""
    return JSONResponse(status_code=status, content={"code": -1, "msg": msg, "data": None})   # 下面 4 个处理器都调它
```

**`error_response()`**：4 个处理器都用它返回，保证格式完全一样。

**① 业务错误：接口里 raise fail(...)**

```python
# app/errors.py（接着写）
def install(app: FastAPI) -> None:
    """统一的错误拦截：不管哪种错误，前端收到的都是 {code: -1, msg, data: null}。"""

    @app.exception_handler(ApiError)             # 登记：抛出 ApiError 时调用下面这个函数
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:   # exc 就是接口里 raise 的那个对象
        return error_response(exc.status, exc.msg)   # 状态码和提示都来自 fail(...) 的两个参数
```

**② 参数校验失败：缺字段、类型不对、长度超限……**

```python
    # app/errors.py（接着写，仍在 install() 里面）
    @app.exception_handler(RequestValidationError)   # 参数没通过校验时，FastAPI 抛这个异常
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]           # 可能有好几条，只取第一条
        field = first["loc"][-1]          # 出错的位置，如 ["body", "title"]，取最后一个 → "title"
        return error_response(422, f"{field}：{first['msg']}")   # 返回 422 和「title：Field required」这样的提示
```

`first["loc"]` 是出错的位置，比如 `["body", "title"]`、`["path", "task_id"]`、`["query", "page"]`，最后一个元素就是字段名。

**③ 框架报的 HTTP 错误：路径不存在 404、请求方法不对 405**

```python
    # app/errors.py（接着写，仍在 install() 里面）
    @app.exception_handler(StarletteHTTPException)   # 访问了不存在的路径、用错了请求方法时抛这个异常
    async def handle_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        msgs = {404: "没有这个接口", 405: "这个接口不支持这种请求方式"}   # 状态码 → 中文提示
        return error_response(exc.status_code, msgs.get(exc.status_code, str(exc.detail)))   # 其他状态码就用原来的英文说明
```

用 FastAPI 自带的 `raise HTTPException(404, ...)` 抛出的错误，也会被 ③ 接住。

**④ 兜底：上面都没接住的异常，基本就是代码 bug**

```python
    # app/errors.py（接着写，仍在 install() 里面）
    @app.exception_handler(Exception)            # Exception 是所有异常的父类，什么都能接住
    async def handle_unknown(request: Request, exc: Exception) -> JSONResponse:
        # 完整的报错堆栈 uvicorn 会打印在终端里，这里不把细节给前端
        return error_response(500, "服务出错了，请稍后再试")   # 只给一句通用提示
```

- **4 个处理器怎么分工**：FastAPI 根据异常的类型，交给对应的处理器。`ApiError` 也是 `Exception` 的子类，但它有专门的 ①，所以走 ①；只有前面三个都没接住的异常，才会落到兜底的 ④。
- **④ 不把报错细节给前端**：报错信息里可能有代码路径、SQL 语句等内部细节。前端只拿到一句通用提示，完整报错去运行 uvicorn 的终端里看。

在 `api_demo.py` 末尾临时加一个会出错的接口，用来试 ④：

```python
# api_demo.py（末尾临时加上，试完删掉）
@app.get("/boom")
def boom() -> dict:
    return {"x": 1 / 0}      # 故意写个 bug
```

换成完整版之后，实际运行结果（全部是同一个格式）：

| 请求 | HTTP | 响应体 |
|---|---|---|
| `GET /tasks/99` | 404 | `{"code": -1, "msg": "没有这个任务", "data": null}` |
| `GET /tasks/abc` | 422 | `{"code": -1, "msg": "task_id：Input should be a valid integer, ...", "data": null}` |
| `POST /tasks`（没传 title） | 422 | `{"code": -1, "msg": "title：Field required", "data": null}` |
| `GET /nope` | 404 | `{"code": -1, "msg": "没有这个接口", "data": null}` |
| `DELETE /tasks/1` | 405 | `{"code": -1, "msg": "这个接口不支持这种请求方式", "data": null}` |
| `GET /boom` | 500 | `{"code": -1, "msg": "服务出错了，请稍后再试", "data": null}` |

参数校验失败用 422 还是 400，团队统一就行，很多项目用 400。如果改成 400，第 3.11 节测试里 `test_empty_title_rejected` 的 422 也要跟着改。

**常用状态码**：

| 状态码 | 含义 |
|---|---|
| 400 | 请求内容不对 |
| 401 | 没登录或登录已过期 |
| 403 | 已登录但没有权限 |
| 404 | 要找的东西不存在 |
| 409 | 状态冲突，比如重名 |
| 422 | 参数校验没过（FastAPI 自动返回） |
| 500 | 服务器出错 |

## 3.6 SQL 基础：PostgreSQL {#sql-basics}

下一节开始用 SQLAlchemy 操作数据库，写的是 Python，但发给数据库的还是 SQL。这一节先不碰 Python，直接在数据库里手写 SQL：建表、增删改查、关联、统计、索引、事务。会了这些，看 SQLAlchemy 打印出来的 SQL、排查慢查询、写统计报表都用得上。

数据库用 **PostgreSQL**（简称 Postgres）：第 3.16 节部署用的 Neon 就是 Postgres，本地和线上用同一种最省事。最后对比一下它和 MySQL 的区别。

### 装好、连上

**1. 装 Postgres 并建一个练习库**：

```bash
brew install postgresql@17          # Mac；Windows 去官网下载安装包
brew services start postgresql@17   # 后台启动，开机自动运行
createdb learn                      # 建一个练习用的库，名字叫 learn
whoami                              # 看一下你的 Mac 用户名，下一步连接时要用
```

**2. 装一个可视化工具**：用 [DBeaver](https://dbeaver.io/) 社区版，免费，Mac、Windows 都能用。

```bash
brew install --cask dbeaver-community   # Mac；Windows 去官网下载安装包
```

**3. 在 DBeaver 里连上 learn 库**：

1. 打开 DBeaver，左上角点「新建数据库连接」（插头图标），选 **PostgreSQL**，下一步。
2. 填连接信息：

   | 项 | 填什么 |
   |---|---|
   | 主机 | `localhost` |
   | 端口 | `5432` |
   | 数据库 | `learn` |
   | 用户名 | 上一步 `whoami` 显示的 Mac 用户名 |
   | 密码 | 空着（brew 装的 Postgres 本机连接不用密码） |

3. 点「测试连接」。第一次会提示下载驱动，点下载；显示「已连接」就对了，点完成。
4. 左边列表里右键这个连接 → SQL 编辑器 → 新建 SQL 脚本，就可以在里面写 SQL 了。

**4. 在 SQL 编辑器里执行**：

- 光标放在某一条 SQL 上，按 `Cmd + Enter`（Windows 是 `Ctrl + Enter`）：只执行这一条，结果显示在下方的表格里。
- 每条 SQL 以分号结尾，一个脚本里可以写很多条，按上面的方式一条一条执行。
- 关键字大小写都行，习惯写大写。
- 左边列表里展开 learn → 架构 → public → 表，能看到建好的表；点开一张表，可以直接看数据、列和索引。

不想在本机装 Postgres，也可以用 Neon 免费版建一个库：在 DBeaver 里同样选 PostgreSQL，把 Neon 给的连接地址里的主机、数据库、用户名、密码分别填进去。

### 建表

```sql
CREATE TABLE users (
    id         serial PRIMARY KEY,                    -- 自增主键：1, 2, 3...
    username   varchar(32) NOT NULL UNIQUE,           -- 不能为空、不能重复
    created_at timestamptz NOT NULL DEFAULT now()     -- 不传就用当前时间
);

CREATE TABLE tasks (
    id         serial PRIMARY KEY,
    user_id    integer NOT NULL REFERENCES users(id) ON DELETE CASCADE,   -- 外键：必须是存在的用户
    title      varchar(100) NOT NULL,
    done       boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),    -- 创建时间
    updated_at timestamptz NOT NULL DEFAULT now()     -- 更新时间：插入时是当前时间，之后每次修改要自己更新
);
```

- `--` 后面是注释。
- **主键** `PRIMARY KEY`：每行的唯一编号，不能重复、不能为空。`serial` 是「整数 + 自动加一」。
- **约束**：`NOT NULL`、`UNIQUE`、`REFERENCES` 都是数据库替你把关，不合规的数据直接拒绝写入，比只在代码里检查可靠。
- **外键** `REFERENCES users(id)`：`tasks.user_id` 必须是 `users` 里存在的 id。`ON DELETE CASCADE`：删用户时，他的任务一起删掉。
- `timestamptz` 是带时区的时间，存的是一个绝对时刻，Postgres 里存时间优先用它。
- **`updated_at` 不会自动变**：`DEFAULT now()` 只在插入时生效，之后修改这一行时，要在 `UPDATE` 里自己写上 `updated_at = now()`（见下面「改」）。用 SQLAlchemy 时可以让它自动更新（第 3.7 节）。

### 增删改查

```sql
-- 增：一次可以插多行
INSERT INTO users (username) VALUES ('alice'), ('bob'), ('carol');
INSERT INTO tasks (user_id, title) VALUES (1, '写笔记'), (1, '学 SQL'), (2, '买菜');

-- RETURNING：插入后直接把新行返回来，不用再查一次
INSERT INTO tasks (user_id, title) VALUES (1, '跑步') RETURNING id, title, done;
--  id | title | done
-- ----+-------+------
--   4 | 跑步  | f

-- 查：WHERE 筛选，ORDER BY 排序（DESC 从大到小）
SELECT id, title, done FROM tasks WHERE user_id = 1 ORDER BY id DESC;
--  id | title  | done
-- ----+--------+------
--   4 | 跑步   | f
--   2 | 学 SQL | f
--   1 | 写笔记 | f

-- 模糊查：% 表示任意几个字符
SELECT id, title FROM tasks WHERE title LIKE '%笔记%';     -- 1 | 写笔记

-- 分页：跳过前 2 条，取 2 条（第 2 页，每页 2 条）
SELECT id, title FROM tasks ORDER BY id LIMIT 2 OFFSET 2;  -- 3 | 买菜、4 | 跑步

-- 改
UPDATE tasks SET done = true, updated_at = now() WHERE id = 1;   -- 顺手更新 updated_at

-- 删
DELETE FROM tasks WHERE id = 4;
```

**`UPDATE` 和 `DELETE` 一定要带 `WHERE`**：不带就是改 / 删整张表，执行前先用同样的 `WHERE` 跑一遍 `SELECT`，确认是哪些行。

约束挡住的写入会直接报错：

```sql
INSERT INTO tasks (user_id, title) VALUES (99, '没有这个人');
-- ERROR:  insert or update on table "tasks" violates foreign key constraint "tasks_user_id_fkey"
-- DETAIL:  Key (user_id)=(99) is not present in table "users".

INSERT INTO users (username) VALUES ('alice');
-- ERROR:  duplicate key value violates unique constraint "users_username_key"
-- DETAIL:  Key (username)=(alice) already exists.
```

### 关联查询：JOIN

任务表里只有 `user_id`，要显示用户名就得把两张表拼起来：

```sql
-- JOIN（内连接）：两边都对得上的才出现
-- 整句意思：列出每条任务，带上它所属用户的用户名，按任务顺序排
SELECT u.username, t.title, t.done   -- ③ 拼好之后取这三列
FROM tasks t                          -- ① 从 tasks 出发，t 是 tasks 的简写
JOIN users u ON u.id = t.user_id      -- ② 每条任务按 user_id 找到它的用户，拼成一行；u 是 users 的简写
ORDER BY t.id;                        -- ④ 按任务 id 排序
--  username | title  | done
-- ----------+--------+------
--  alice    | 写笔记 | t
--  alice    | 学 SQL | f
--  bob      | 买菜   | f
-- carol 没有任务，对不上，不出现

-- LEFT JOIN（左连接）：左边的表（FROM 后面那张）每行都出现，右边对不上的列填 NULL
-- 整句意思：列出所有用户和各自的任务，没有任务的用户也要列出来
-- 和上一句的区别：上一句从任务出发，只看得到有任务的人；这句从用户出发，一个用户都不漏
SELECT u.username, t.title            -- ③ 拼好之后取这两列
FROM users u                          -- ① 这次从 users 出发，users 是左边的表
LEFT JOIN tasks t ON t.user_id = u.id -- ② 每个用户找自己的任务：有几条拼几行，一条都没有也留一行，t 的列全是 NULL
ORDER BY u.id, t.id;                  -- ④ 先按用户排，同一个用户再按任务排
--  username | title
-- ----------+--------
--  alice    | 写笔记
--  alice    | 学 SQL
--  bob      | 买菜
--  carol    |            ← carol 没有任务，title 是 NULL
```

规则记住就行：

1. `JOIN` 就是 `INNER JOIN`：只留两边都对得上的行。
2. `LEFT JOIN`：左边的表全留，右边没有就是 NULL。「列出所有用户，包括还没数据的」就用它，用 `JOIN` 会把 carol 漏掉。
3. `ON` 写拼接条件，一般是「外键 = 主键」。
4. 两张表有同名列（比如都有 `id`）时，必须写 `t.id`、`u.id` 区分。

**逗号写法（老式多表查询）就是内连接**，结果和上面的 `JOIN` 一模一样：

```sql
-- FROM 后面用逗号列多张表，拼接条件写在 WHERE 里
SELECT u.username, t.title, t.done
FROM users u, tasks t
WHERE u.id = t.user_id
ORDER BY t.id;
--  username | title  | done
-- ----------+--------+------
--  alice    | 写笔记 | t
--  alice    | 学 SQL | f
--  bob      | 买菜   | f
-- 和 JOIN 一样，carol 不出现；想要 carol 只能用 LEFT JOIN

-- 漏写 WHERE：每个用户和每条任务两两组合，3 × 3 = 9 行
SELECT u.username, t.title FROM users u, tasks t ORDER BY u.id, t.id;
--  username | title
-- ----------+--------
--  alice    | 写笔记
--  alice    | 学 SQL
--  alice    | 买菜
--  bob      | 写笔记
--  bob      | 学 SQL
--  bob      | 买菜
--  carol    | 写笔记
--  carol    | 学 SQL
--  carol    | 买菜
```

`LEFT JOIN` 的常见用法：找出「没有任务的用户」：

```sql
SELECT u.username
FROM users u
LEFT JOIN tasks t ON t.user_id = u.id   -- carol 拼出来那行，t 的列都是 NULL
WHERE t.id IS NULL;                     -- 只留对不上的行（判断 NULL 要用 IS NULL，不能写 = NULL）
--  username
-- ----------
--  carol
```

### 分组统计：GROUP BY

```sql
-- 每个用户有几个任务、完成了几个
SELECT u.username,
       count(t.id)                       AS total,
       count(t.id) FILTER (WHERE t.done) AS done
FROM users u
LEFT JOIN tasks t ON t.user_id = u.id
GROUP BY u.id, u.username
ORDER BY total DESC;
--  username | total | done
-- ----------+-------+------
--  alice    |     2 |    1
--  bob      |     1 |    0
--  carol    |     0 |    0

-- HAVING：对分组后的结果再筛选（WHERE 是分组前筛行）
SELECT user_id, count(*) AS total FROM tasks GROUP BY user_id HAVING count(*) >= 2;
--  user_id | total
-- ---------+-------
--        1 |     2
```

- `GROUP BY` 把同一个用户的行归成一组，`count`、`sum`、`max`、`avg` 对每组算一个值。
- `SELECT` 里除了聚合函数，其他列都要写进 `GROUP BY`。
- `count(t.id)` 只数不是 NULL 的，所以 carol 是 0；写 `count(*)` 会把 LEFT JOIN 补出来的那行也算上，变成 1。
- `FILTER (WHERE ...)` 是 Postgres 的写法，「只数满足条件的」。通用写法是 `sum(CASE WHEN t.done THEN 1 ELSE 0 END)`，MySQL 只能用这种。

### 索引：让查询变快

没有索引时，按 `title` 查要把整张表一行行看一遍。先造 30 万条数据：

```sql
-- generate_series 生成 1～300000 的数字，一条语句插 30 万行
INSERT INTO tasks (user_id, title)
SELECT (i % 3) + 1, '任务 ' || i FROM generate_series(1, 300000) AS i;
```

`EXPLAIN ANALYZE` 会真的执行一次查询，并告诉你数据库是怎么查的、花了多久：

```sql
-- 后半句是普通查询：找出标题是「任务 299999」的那一行（造数据时的第 299999 条，在表很靠后）
-- 前面加 EXPLAIN ANALYZE：查询照常真的执行，但不看查出来的数据，改为报告「怎么查的、花了多久」
-- （只写 EXPLAIN 不带 ANALYZE：只给计划、不执行；带 ANALYZE 是真执行，别加在 DELETE / UPDATE 前面乱试）
EXPLAIN ANALYZE SELECT id, title FROM tasks WHERE title = '任务 299999';
--  Parallel Seq Scan on tasks ...      ← Seq Scan = 全表扫描，一行行看过去；Parallel = 开了几个进程分头扫
--    Rows Removed by Filter: 150001    ← 看过但不符合条件、被扔掉的行数（每个进程平均的，几个进程加起来就是整张表）
--  Execution Time: 7.625 ms            ← 实际耗时：为了找 1 行，把 30 万行全看了一遍

-- 给 title 建索引：数据库另外存一份按 title 排好序的目录，记着每个标题在哪一行
-- idx_tasks_title 是索引名，自己起；tasks (title) 表示给 tasks 表的 title 列建
CREATE INDEX idx_tasks_title ON tasks (title);

-- 同一条查询再看一次
EXPLAIN ANALYZE SELECT id, title FROM tasks WHERE title = '任务 299999';
--  Index Scan using idx_tasks_title on tasks ...   ← Index Scan = 走索引，在目录里直接定位到那一行，不用全表看
--  Execution Time: 0.023 ms                        ← 从 7.6 毫秒降到 0.02 毫秒
```

- `Seq Scan` 是全表扫描，`Index Scan` 是走索引。同一条查询从 7.6 毫秒变成 0.02 毫秒，数据越多差得越多。
- 主键和 `UNIQUE` 会自动建索引（DBeaver 里展开 `users` 表的「索引」能看到 `users_username_key`）。**Postgres 不会给外键自动建索引**，`tasks.user_id` 经常拿来筛选，要自己建：`CREATE INDEX ON tasks (user_id);`。
- 经常一起筛选的列可以建联合索引：`CREATE INDEX ON tasks (user_id, done);`，查询条件里带上最左边的 `user_id` 才能充分用上它。
- 索引不是越多越好：每次写入都要同步更新索引，表也会变大。给 `WHERE`、`JOIN`、`ORDER BY` 里常用的列建。
- 分页用 `OFFSET` 时，数据库其实要先数过前面那些行再扔掉，`OFFSET 100000` 会越来越慢。数据很多时改成「上一页最后一个 id 之后的 20 条」：`WHERE id < 上一页最小id ORDER BY id DESC LIMIT 20`。

### 事务：几条 SQL 要么都成功，要么都不算

```sql
BEGIN;                                              -- 开始事务
UPDATE tasks SET done = true WHERE user_id = 1;     -- UPDATE 100002
SELECT count(*) FROM tasks WHERE user_id = 1 AND done;   -- 100002：事务里能看到改动
ROLLBACK;                                           -- 撤销，改动全部作废

SELECT count(*) FROM tasks WHERE user_id = 1 AND done;   -- 1：回到改之前
```

- 确定没问题就把 `ROLLBACK` 换成 `COMMIT`，改动才真正保存，别的连接才看得到。
- 不写 `BEGIN` 时，每条语句自己就是一个事务，执行完自动提交。
- 转账这类「扣 A 的钱、加 B 的钱」必须放在一个事务里，中间出错就回滚，不会出现只扣不加。SQLAlchemy 的 `session.commit()` / `session.rollback()`，背后都是这个。
- 手动练习时，改数据前先 `BEGIN`，看结果对了再 `COMMIT`，不对就 `ROLLBACK`，比直接改安全。

### 有就更新、没有就插入：upsert

记录每人每天的学习时长：同一个人同一天只有一行，第一次插入，之后累加。

```sql
CREATE TABLE daily_stats (
    user_id integer NOT NULL REFERENCES users(id),
    day     date    NOT NULL,
    seconds integer NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day)          -- 联合主键：(用户, 日期) 不能重复
);

-- 跑两遍
INSERT INTO daily_stats (user_id, day, seconds) VALUES (1, '2026-11-13', 60)
ON CONFLICT (user_id, day) DO UPDATE SET seconds = daily_stats.seconds + EXCLUDED.seconds;

SELECT * FROM daily_stats;
--  user_id |    day     | seconds
-- ---------+------------+---------
--        1 | 2026-11-13 |     120     ← 第二次没有新插一行，而是累加

-- 已经有就什么都不做
INSERT INTO users (username) VALUES ('alice') ON CONFLICT (username) DO NOTHING;   -- INSERT 0 0
```

- `ON CONFLICT (user_id, day)`：这两列撞了（违反主键或唯一约束）就不插入，改成执行后面的 `UPDATE`。
- `EXCLUDED` 指「这次想插入但被挡住的那行」，`daily_stats.seconds` 是表里原来的值。
- 先查有没有再决定插入还是更新，两个请求同时来时可能都查到「没有」，结果插两行或报错。upsert 一条语句由数据库保证不会撞。

### 和 MySQL 的区别

两者大部分 SQL 一样，上面的建表、增删改查、JOIN、GROUP BY、事务在 MySQL 里基本照抄就能用。主要差别：

| | PostgreSQL | MySQL |
|---|---|---|
| 自增主键 | `serial` 或 `GENERATED ALWAYS AS IDENTITY` | `AUTO_INCREMENT` |
| 修改时自动更新时间 | 不支持，`UPDATE` 时自己写 `updated_at = now()`，或者用触发器 | 列定义加 `ON UPDATE CURRENT_TIMESTAMP` 就行 |
| 插入后拿新行 | `RETURNING id, ...` | 不支持，用 `LAST_INSERT_ID()` 拿 id 再查一次 |
| upsert | `ON CONFLICT (列) DO UPDATE SET ...` / `DO NOTHING` | `ON DUPLICATE KEY UPDATE ...`，不能指定按哪个约束 |
| 按条件计数 | `count(*) FILTER (WHERE ...)` | `sum(CASE WHEN ... THEN 1 ELSE 0 END)` |
| 字符串比较 | 区分大小写：`'Alice' = 'alice'` 是假，不区分用 `ILIKE` | 默认不区分大小写 |
| 布尔 | 真正的 `boolean` | `BOOLEAN` 其实是 `tinyint(1)`，存 0 / 1 |
| 名字加引号 | 双引号 `"order"` | 反引号 `` `order` `` |
| 外键索引 | 不自动建，要自己建 | InnoDB 自动建 |
| 建表、改表能回滚 | 能，`CREATE TABLE` 也在事务里 | 不能，执行就立即提交 |
| JSON | `jsonb`，能建索引、查询能力强 | `JSON`，能用但功能少一些 |
| SQLAlchemy 地址 | `postgresql+psycopg://...` | `mysql+pymysql://...` |

**怎么选**：
- 新项目、Python 项目更多选 Postgres：类型和约束更严格，`jsonb`、`RETURNING`、`ON CONFLICT` 这些写后端很顺手；Neon、Supabase 等云服务也都是 Postgres。
- MySQL 在国内互联网公司用得非常多，很多老项目、云厂商的默认选项是它。进了公司用哪个看团队。
- 用 SQLAlchemy 时，大部分差异被它屏蔽了，换库主要是换连接地址（第 3.15 节有实操）。两个都会一点最好，会了 Postgres 再学 MySQL 很快。

### 下一节：SQL 交给 SQLAlchemy 写

上面的 SQL，到了 Python 里会变成这样：

| SQL | SQLAlchemy（下一节开始讲） |
|---|---|
| `CREATE TABLE tasks (...)` | `class Task(Base)` 加 `Base.metadata.create_all(engine)` |
| `INSERT INTO tasks ...` | `session.add(Task(title=...))` |
| `SELECT ... WHERE done = false` | `select(Task).where(Task.done == False)` |
| `COMMIT` / `ROLLBACK` | `session.commit()` / `session.rollback()` |

练习项目直接用上面装好的 Postgres，再建两个库：

```bash
createdb todo         # 接口用的库，第 3.7 节开始连它
createdb todo_test    # 测试专用的库，第 3.11 节用（测试会清空它，所以和 todo 分开）
```

在 DBeaver 里照「装好、连上」第 3 步再建一个连接，数据库填 `todo`，代码写进去的数据随时能打开表看到。

## 3.7 连数据库：SQLAlchemy {#sqlalchemy}

**一个类 = 一张表，一个对象 = 一行，一个属性 = 一列。**

**先把配置放进 `.env`**：数据库地址这类配置不写死在代码里。在 `todo-api/` 下新建 `.env`：

```
# .env：自己电脑上真正用的配置
DATABASE_URL=postgresql+psycopg://localhost:5432/todo
```

`.env` 里以后会有密码（比如连云数据库的地址里就带密码），**不能提交**，要写进 `.gitignore`：

```
# .gitignore
.env
```

这样 git 仓库里就没有 `.env` 了，别人拉下代码不知道要配哪些项。所以另外建一个 `.env.example` 提交上去，**两个文件的作用不同**：

- `.env`：自己用的真实值，不提交。
- `.env.example`：只列出「要配哪些项」，值写示例或占位，提交到仓库。别人复制一份改名成 `.env`，再改成自己的值就能用。

```
# .env.example：提交到仓库的模板
# 格式：postgresql+psycopg://用户名:密码@主机:端口/库名
# 本机 brew 装的 Postgres 不用写用户名和密码，下面这行直接能用
DATABASE_URL=postgresql+psycopg://localhost:5432/todo
```

现在两个文件里 `DATABASE_URL` 那行一样，是因为本机连接不用密码，示例值就是能用的值。以后换成带密码的云数据库，或者加了密钥这类配置，`.env` 写真实值，`.env.example` 只写 `SECRET_KEY=换成你自己的` 这样的占位。

```python
# app/db.py
from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()      # 读当前目录的 .env，把里面的配置放进环境变量（已经设置过的不覆盖）

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://localhost:5432/todo")   # 读环境变量，读不到用默认值

engine = create_engine(DATABASE_URL)          # 引擎：管理和数据库的连接
SessionLocal = sessionmaker(engine, autoflush=False, expire_on_commit=False)  # 会话工厂


class Base(DeclarativeBase):
    """所有表模型的父类，固定写法。"""
    pass
```

```python
# app/models.py
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Task(Base):
    __tablename__ = "tasks"                       # 数据库里的表名

    id: Mapped[int] = mapped_column(Integer, primary_key=True)          # 主键，自增
    title: Mapped[str] = mapped_column(String(200), nullable=False)     # 必填
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    note: Mapped[str | None] = mapped_column(String(500))               # | None = 可以为空
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now,   # 新建时填，修改时自动刷新
    )
```

**表定义里的几个点**：

- `Mapped[类型]`：Python 里这一列是什么类型。
- `mapped_column(...)`：数据库里这一列的定义。
- `default=_now`：插入时没给值，就调用 `_now()`。注意传的是函数本身，不加括号；写成 `default=datetime.now(UTC)` 会在程序启动时就算好一个固定时间，所有数据都一样。
- `onupdate=_now`：这一行被修改、提交时，自动调用 `_now()` 更新这一列。`updated_at` 就靠它：新建时和创建时间基本一样（各调一次 `_now()`，可能差几微秒），之后每次改动都会刷新。
- **表结构改了要删库重建**：`create_all` 只会建不存在的表，不会给已有的表加列。已经跑过旧版本的话，先删库重建再启动：`dropdb todo && createdb todo`，否则会报 `column tasks.updated_at does not exist`。正式项目用 alembic 处理这种改动（第 3.15 节）。

## 3.8 增删改查：Session {#session}

**Session** 是你和数据库之间的一次「会话」：在里面查、加、改、删数据，它会记住你改了什么，等你 `commit()` 时一次性写进数据库。

- **增删改**：`session.add(...)`、改属性、`session.delete(...)` 都只是先记下来，**`commit()` 才真正写进数据库**。没 commit 就关闭会话，改动全部作废。
- **查**：`session.get(...)`、`session.scalars(...)` 会立即查数据库，把结果变成 `Task` 对象。查询不改数据，所以不用 commit。

下面按「增、查、改、删」分块写，几块代码依次放进同一个文件 `crud_demo.py`。每个接口都用 `with SessionLocal() as session:` 开一个会话，`with` 结束自动关闭。

### 准备：建 app、建表

```python
# crud_demo.py（放在 todo-api/ 下）：每个接口演示一种数据库操作
from fastapi import FastAPI
from sqlalchemy import select

from app import errors
from app.db import Base, SessionLocal, engine
from app.errors import fail
from app.models import Task
from app.response import success
from app.schemas import TaskOut              # 第 3.3 节定义的「返回给前端的一条任务」

app = FastAPI()
errors.install(app)
Base.metadata.create_all(engine)           # 建表（表已存在就跳过）
```

- **`TaskOut.model_validate(task)`**：下面每个接口都用它把数据库里的 `Task` 对象转成返回给前端的 `TaskOut`（第 3.3 节末尾讲过，`TaskOut` 加了 `from_attributes=True` 才能这样用）。
- **为什么不能直接 `success(task)`**：`Task` 是 SQLAlchemy 的数据库对象，FastAPI 不知道怎么把它转成 JSON，会报错返回 500。转成 `TaskOut` 还有一个好处：只输出 `TaskOut` 里定义的字段，以后表里加了不该给前端看的列，也不会被带出去。

四块都写完后，在 `todo-api/` 目录启动，到 `/docs` 里按顺序试。每块下面是按顺序实际执行的结果：

```bash
uvicorn crud_demo:app --reload
```

### 增：add + commit

```python
# crud_demo.py（接着写）
# 增：POST /tasks?title=写笔记
@app.post("/tasks", status_code=201)
def create_task(title: str, note: str | None = None) -> dict:
    with SessionLocal() as session:        # 开一个会话，with 结束自动关闭
        # 先查有没有同名的，分三步：
        stmt = select(Task).where(Task.title == title)   # ① 只是拼好 SQL，还没查：SELECT * FROM tasks WHERE title = '写笔记'
        result = session.scalars(stmt)                   # ② 这时才把上面的 SELECT 发给数据库执行；scalars：结果每行本来是 (Task,) 这样的元组，去掉这层，直接拿到 Task 对象
        same = result.one_or_none()                      # ③ 要求结果最多一条：0 条给 None，1 条给那个对象，多条直接报错
        if same is not None:
            raise fail(409, "已经有同名任务了")

        task = Task(title=title, note=note)
        session.add(task)                  # 只是记下「要插入」，还没写进数据库
        session.commit()                   # INSERT INTO tasks (title, note, ...) VALUES ('写笔记', NULL, ...)，真正写进数据库，task.id 这时有值了
        return success(TaskOut.model_validate(task), msg="创建成功")
```

| 请求 | HTTP | 响应体 |
|---|---|---|
| `POST /tasks?title=写笔记` | 201 | `{"code": 200, "msg": "创建成功", "data": {"id": 1, "title": "写笔记", "done": false, "note": null, "created_at": "2026-11-19T09:34:33.379495Z", "updated_at": "2026-11-19T09:34:33.379498Z"}}` |
| `POST /tasks?title=读书` | 201 | `{"code": 200, "msg": "创建成功", "data": {"id": 2, "title": "读书", "done": false, "note": null, "created_at": "2026-11-19T09:34:35.120331Z", "updated_at": "2026-11-19T09:34:35.120334Z"}}` |
| `POST /tasks?title=跑步&note=5 公里` | 201 | `{"code": 200, "msg": "创建成功", "data": {"id": 3, "title": "跑步", "done": false, "note": "5 公里", "created_at": "2026-11-19T09:34:37.845102Z", "updated_at": "2026-11-19T09:34:37.845105Z"}}` |
| `POST /tasks?title=读书` | 409 | `{"code": -1, "msg": "已经有同名任务了", "data": null}` |

时间是示例，按你实际运行的时刻。**返回的时间有两种写法**：刚创建的任务返回 `2026-11-19T09:34:33.379495Z`，从库里查出来的返回 `2026-11-19T17:34:33.379495+08:00`。创建时返回的是 Python 里 `_now()` 算的 UTC 时间（`Z` 结尾）；查询时 Postgres 按自己设置的时区（装的时候跟电脑一样，国内是 `Asia/Shanghai`）换算好再返回。两种写法是同一个时刻，前端用 `new Date(...)` 解析结果一样。

### 查：列表和单条

查列表分三步看，一次只多一样东西。

**① 先查全部**（先看懂，不用写进文件）：

```python
@app.get("/tasks")
def list_tasks() -> dict:
    with SessionLocal() as session:
        tasks = session.scalars(select(Task)).all()     # 查出所有任务，相当于 SELECT * FROM tasks
        return success([TaskOut.model_validate(t) for t in tasks])    # 每个都转成 TaskOut 再返回
```

**② 加一个筛选：只看没完成的**。在 `select` 后面加 `.where(...)`，相当于 SQL 的 `WHERE`：

```python
select(Task).where(Task.done == False)     # SELECT * FROM tasks WHERE done = false
```

**③ 让前端决定要不要筛选**：把 `done` 做成可选参数，传了 `?done=false` 才加条件，不传就查全部。写进文件的是这个版本：

```python
# crud_demo.py（接着写）
# 查列表：GET /tasks 或 GET /tasks?done=false
@app.get("/tasks")
def list_tasks(done: bool | None = None) -> dict:
    with SessionLocal() as session:
        stmt = select(Task)                       # SELECT * FROM tasks（只是拼好，这时还没查）
        if done is not None:                      # 前端传了 done 才加条件
            stmt = stmt.where(Task.done == done)     # 加上 WHERE done = false
        tasks = session.scalars(stmt).all()       # 这时才真正去数据库查：SELECT * FROM tasks WHERE done = false
        return success([TaskOut.model_validate(t) for t in tasks])
```

`stmt` 是「查询语句」的意思：`select(...)`、`.where(...)` 只是在拼这条语句，`session.scalars(stmt)` 才把它发给数据库。所以可以先拼好、再按条件往上加，最后查一次。

排序（`.order_by`）、只取几条（`.limit`）、数总数，都是在这个基础上再加，第 3.10 节用到时再讲。

```python
# crud_demo.py（接着写）
# 查一条：GET /tasks/1
@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    with SessionLocal() as session:
        task = session.get(Task, task_id)                 # SELECT * FROM tasks WHERE id = 1，按主键查，没有就是 None
        if task is None:
            raise fail(404, "没有这个任务")
        return success(TaskOut.model_validate(task))
```

| 请求 | HTTP | 响应体 |
|---|---|---|
| `GET /tasks` | 200 | `{"code": 200, "msg": "ok", "data": [{"id": 1, "title": "写笔记", "done": false, "note": null, "created_at": "2026-11-19T17:34:33.379495+08:00", "updated_at": "2026-11-19T17:34:33.379498+08:00"}, {"id": 2, "title": "读书", "done": false, "note": null, "created_at": "2026-11-19T17:34:35.120331+08:00", "updated_at": "2026-11-19T17:34:35.120334+08:00"}, {"id": 3, "title": "跑步", "done": false, "note": "5 公里", "created_at": "2026-11-19T17:34:37.845102+08:00", "updated_at": "2026-11-19T17:34:37.845105+08:00"}]}` |
| `GET /tasks/1` | 200 | `{"code": 200, "msg": "ok", "data": {"id": 1, "title": "写笔记", "done": false, "note": null, "created_at": "2026-11-19T17:34:33.379495+08:00", "updated_at": "2026-11-19T17:34:33.379498+08:00"}}` |
| `GET /tasks/99` | 404 | `{"code": -1, "msg": "没有这个任务", "data": null}` |

### 改：改属性 + commit

```python
# crud_demo.py（接着写）
# 改：PATCH /tasks/1/done
@app.patch("/tasks/{task_id}/done")
def finish_task(task_id: int) -> dict:
    with SessionLocal() as session:
        task = session.get(Task, task_id)            # SELECT * FROM tasks WHERE id = 1
        if task is None:
            raise fail(404, "没有这个任务")
        task.done = True                   # 直接改属性，还没写进数据库
        session.commit()                   # commit 时自动生成 UPDATE tasks SET done = true, updated_at = ... WHERE id = 1
        return success(TaskOut.model_validate(task), msg="已完成")
```

| 请求 | HTTP | 响应体 |
|---|---|---|
| `PATCH /tasks/1/done` | 200 | `{"code": 200, "msg": "已完成", "data": {"id": 1, "title": "写笔记", "done": true, "note": null, "created_at": "2026-11-19T17:34:33.379495+08:00", "updated_at": "2026-11-19T09:35:10.502117Z"}}` |
| `GET /tasks?done=false` | 200 | `{"code": 200, "msg": "ok", "data": [{"id": 2, "title": "读书", "done": false, "note": null, "created_at": "2026-11-19T17:34:35.120331+08:00", "updated_at": "2026-11-19T17:34:35.120334+08:00"}, {"id": 3, "title": "跑步", "done": false, "note": "5 公里", "created_at": "2026-11-19T17:34:37.845102+08:00", "updated_at": "2026-11-19T17:34:37.845105+08:00"}]}` |

### 删：delete + commit

```python
# crud_demo.py（接着写）
# 删：DELETE /tasks/1
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> dict:
    with SessionLocal() as session:
        task = session.get(Task, task_id)            # SELECT * FROM tasks WHERE id = 1
        if task is None:
            raise fail(404, "没有这个任务")
        session.delete(task)               # 记下「要删除」，还没删
        session.commit()                   # commit 时生成 DELETE FROM tasks WHERE id = 1
        return success(msg="删除成功")
```

| 请求 | HTTP | 响应体 |
|---|---|---|
| `DELETE /tasks/2` | 200 | `{"code": 200, "msg": "删除成功", "data": null}` |
| `GET /tasks` | 200 | `{"code": 200, "msg": "ok", "data": [{"id": 1, "title": "写笔记", "done": true, "note": null, "created_at": "2026-11-19T17:34:33.379495+08:00", "updated_at": "2026-11-19T17:35:10.502117+08:00"}, {"id": 3, "title": "跑步", "done": false, "note": "5 公里", "created_at": "2026-11-19T17:34:37.845102+08:00", "updated_at": "2026-11-19T17:34:37.845105+08:00"}]}` |

### 小结

常用写法：

| 想做什么 | 写法 |
|---|---|
| 按主键取一条 | `session.get(Task, 1)`，没有返回 `None` |
| 条件查询 | `select(Task).where(Task.done == False)` |
| 多个条件 | `.where(条件1, 条件2)` 是「且」 |
| 排序 / 条数 / 跳过 | `.order_by(Task.id.desc())`、`.limit(20)`、`.offset(40)` |
| 拿列表 | `session.scalars(stmt).all()` |
| 拿一条 | `session.scalars(stmt).one_or_none()` 或 `session.scalar(stmt)` |
| 计数 | `session.scalar(select(func.count()).select_from(Task))` |
| 新增 | `session.add(obj)` |
| 修改 | 直接改属性：`task.done = True` |
| 删除 | `session.delete(obj)` |
| 提交 / 撤销 | `session.commit()` / `session.rollback()` |

**想看 SQLAlchemy 实际发了什么 SQL**：在 `db.py` 里给 `create_engine` 加上 `echo=True`：

```python
# app/db.py
engine = create_engine(DATABASE_URL, echo=True)   # echo=True：把每条 SQL 打印到终端，调试用，上线前去掉
```

重启服务，调一次 `POST /tasks?title=写笔记`，终端会打出这样的内容（简化过，去掉了时间、参数这些细节）：

```text
BEGIN (implicit)                                  ← with 开会话，开始一个事务
SELECT tasks.id, tasks.title, ... FROM tasks
WHERE tasks.title = ?                             ← 查同名：session.scalars(...) 立刻就查了
INSERT INTO tasks (title, done, note, ...) VALUES (?, ?, ?, ...)   ← commit 时才插入
COMMIT                                            ← 真正写进数据库
```

`session.add(task)` 那一行什么 SQL 都没发，`INSERT` 是到 `commit()` 才出现的。改和删也一样：

```text
PATCH /tasks/1/done                    DELETE /tasks/1
SELECT ... WHERE tasks.id = ?          SELECT ... WHERE tasks.id = ?    ← session.get 立刻查
UPDATE tasks SET done=? WHERE ...      DELETE FROM tasks WHERE ...      ← commit 时才发
COMMIT                                 COMMIT
```

`?` 是参数的占位符，真正的值（比如 `'写笔记'`）会在下一行单独打印出来。用 Postgres 时占位符长得不一样（类似 `%(title)s`），意思相同。

**发现问题了吗**：每个接口都在重复 `with SessionLocal() as session:`、查不到就 `raise fail(404, ...)`。下一节用依赖注入把「开会话」交给 FastAPI，第 3.10 节再把「查不到就 404」抽成 `load_task()`。

## 3.9 依赖注入：拿到数据库会话 {#dependency-injection}

每个接口都需要一个 Session，但不想每个接口都重复写「创建、提交、出错回滚、关闭」。把这套流程写成一个函数，接口参数里声明「我要一个 Session」，FastAPI 每次请求都会调用它，把结果传进来。这就是**依赖注入**。

在 `app/db.py` 末尾补上：

```python
# app/db.py（续）
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session


def db_session() -> Iterator[Session]:
    """一个请求一个会话：正常结束提交，出错回滚，最后关闭。"""
    session = SessionLocal()
    try:
        yield session          # ① 把 session 交给接口，在这里暂停
        session.commit()       # ② 接口正常返回后，从这里继续：commit，这次请求的 INSERT / UPDATE / DELETE 才真正写进去
    except BaseException:
        session.rollback()     # ③ 接口抛了异常，撤销这次请求的所有修改
        raise
    finally:
        session.close()        # ④ 不管怎样都关闭


Db = Annotated[Session, Depends(db_session)]   # 起个短名字，接口里写 session: Db 就行
```

- **`yield`**：函数执行到 `yield` 时交出一个值并暂停，之后从暂停的地方接着跑。执行顺序：① → 接口函数（一直到 return）→ ② 或 ③ → ④。注意：接口 return 的时候，返回给前端的内容就已经定了，② 出错也改不了它。
- **`Annotated[Session, Depends(db_session)]`**：「类型是 Session，值由 `db_session` 提供」。

**写数据的接口要自己 commit**：只要接口会改数据库（增、改、删），就在接口里、`return` 之前写一行 `session.commit()`，不要等 ② 帮你提交。

```python
# ❌ 不自己 commit：先说成功，再去存
@app.post("/tasks")
def create_task(title: str, session: Db) -> dict:
    task = Task(title=title)
    session.add(task)                                  # 只是记下「要插入」，INSERT 要等 commit 才发
    return success(TaskOut.model_validate(task), msg="创建成功")      # 响应内容这时已经定了
    # 之后 ② 才 commit；万一失败，数据没存进去，前端却已经拿到「创建成功」


# ✅ 自己 commit：先存，存好了再说成功
@app.post("/tasks")
def create_task(title: str, session: Db) -> dict:
    task = Task(title=title)
    session.add(task)                                # 记下「要插入」
    session.commit()                                   # INSERT INTO tasks ...，真正存进数据库；失败就在这里抛异常，前端收到的是错误
    return success(TaskOut.model_validate(task), msg="创建成功")      # 能走到这里，说明真的存好了
```

| 接口 | 改数据库吗 | 要自己 commit 吗 |
|---|---|---|
| 增 `POST` | 改 | 要 |
| 改 `PATCH` / `PUT` | 改 | 要 |
| 删 `DELETE` | 改 | 要 |
| 查 `GET` | 不改 | 不用 |

写数据的接口自己提交之后，② 那里已经没东西可提交了，只是兜底。`db_session` 真正省事的是另外两件：出错时 ③ 自动回滚，最后 ④ 一定关闭会话，不用每个接口自己写。

接口里使用：参数写 `session: Db`，FastAPI 每次请求先调用 `db_session()` 开好会话再传进来，接口里不用再写 `with SessionLocal() as session:`。拿第 3.8 节的「查一条」和「增」改一下：

```python
# crud_demo.py（改成用依赖注入）
from app.db import Db


# 查一条：GET /tasks/1（只读，不用 commit）
@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Db) -> dict:
    task = session.get(Task, task_id)        # SELECT * FROM tasks WHERE id = 1；session 已经准备好了，直接用
    if task is None:
        raise fail(404, "没有这个任务")
    return success(TaskOut.model_validate(task))
    # 返回后 db_session 接着跑 ②（这里没改数据，提交了也没事）和 ④ 关闭


# 增：POST /tasks?title=写笔记（写数据，返回前自己 commit）
@app.post("/tasks", status_code=201)
def create_task(title: str, session: Db, note: str | None = None) -> dict:
    same = session.scalars(select(Task).where(Task.title == title)).one_or_none()   # SELECT * FROM tasks WHERE title = '写笔记'，最多一条
    if same is not None:
        raise fail(409, "已经有同名任务了")   # 抛异常 → db_session 走 ③ 回滚，再 ④ 关闭

    task = Task(title=title, note=note)
    session.add(task)                                # 记下「要插入」
    session.commit()                          # INSERT INTO tasks ...；自己提交：提交失败会直接报错，前端不会收到「创建成功」
    return success(TaskOut.model_validate(task), msg="创建成功")
```

和第 3.8 节比，接口里少了一层 `with`，开会话、出错回滚、关闭都交给了 `db_session`。返回的响应体和第 3.8 节完全一样。

`session: Db` 没有默认值，要写在有默认值的参数（`note: str | None = None`）前面，这是 Python 函数参数的规定。

## 3.10 完整的 todo 接口 {#todo-api}

| 方法 | 路径 | 作用 | 成功时 |
|---|---|---|---|
| GET | `/tasks?done=false&limit=20` | 列表，可按是否完成筛选 | 200 |
| POST | `/tasks` | 新建；同名未完成任务已存在则 409 | 201 |
| GET | `/tasks/{id}` | 详情；不存在则 404 | 200 |
| PATCH | `/tasks/{id}/done` | 标记完成 | 200 |
| DELETE | `/tasks/{id}` | 删除 | 200 |

列表接口要同时返回「这一页的任务」和「总共几条」，在 `schemas.py` 末尾加一个模型：

```python
# app/schemas.py（末尾加上）
class TaskList(BaseModel):
    items: list[TaskOut]      # 模型可以嵌套：items 是 TaskOut 的列表
    total: int                # 一共多少条
```

下面按「准备、查列表、增、查一条、改、删」分块写，几块代码依次放进同一个文件 `app/main.py`。

### 准备：导入、建 app、抽出 load_task

```python
# app/main.py
from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import func, select                 # func.count() 用来数条数
from sqlalchemy.orm import Session                  # load_task 的参数类型

from app import errors
from app.db import Base, Db, engine                 # Db：依赖注入拿会话（第 3.9 节）
from app.errors import fail, task_not_found         # 业务错误（第 3.5 节）
from app.models import Task                         # 表模型（第 3.7 节）
from app.response import success                    # 统一响应格式（第 3.4 节）
from app.schemas import TaskCreate, TaskList, TaskOut   # 请求体、列表响应、单条响应

app = FastAPI(title="todo-api")                     # title 显示在 /docs 页面顶部
errors.install(app)                                 # 登记错误处理器，所有错误都返回 {code: -1, msg, data: null}
Base.metadata.create_all(engine)   # 练习用：启动时自动建表；正式项目用 alembic 管理表结构（第 3.15 节）


def load_task(session: Session, task_id: int) -> Task:
    """按 id 取任务，没有就报 404。好几个接口都要用，抽成函数。"""
    task = session.get(Task, task_id)               # SELECT * FROM tasks WHERE id = 1，按主键查一条
    if task is None:                                # 查不到
        raise task_not_found()                      # 抛 404「没有这个任务」，调用它的接口不会再往下执行
    return task                                     # 查到了就返回 Task 对象
```

- **`load_task`**：第 3.8 节里「查一条、改、删」都在重复「`session.get` → 是 None 就 404」，抽成一个函数，后面三个接口各用一行就行。
- 接口参数都写 `session: Db`（第 3.9 节），不再写 `with SessionLocal() as session:`。

### 查列表：GET /tasks

```python
# app/main.py（接着写）
@app.get("/tasks")
def list_tasks(session: Db, done: bool | None = None, limit: int = 20) -> dict:
    stmt = select(Task).order_by(Task.id.desc()).limit(limit)   # SELECT * FROM tasks ORDER BY id DESC LIMIT 20（只是拼好，还没查）
    if done is not None:                                        # 前端传了 ?done=... 才筛选
        stmt = stmt.where(Task.done == done)                    # 加上 WHERE done = false
    tasks = session.scalars(stmt).all()                         # 这时才执行上面拼好的 SELECT，拿到 Task 对象列表
    total = session.scalar(select(func.count()).select_from(Task))   # SELECT count(*) FROM tasks，只取这一个数字（没带 done 条件）
    items = [TaskOut.model_validate(t) for t in tasks]          # 每个 Task 对象转成 TaskOut，只留给前端的字段
    return success(TaskList(items=items, total=total or 0))     # 返回 {code, msg, data: {items: [...], total: 3}}
```

比第 3.8 节多了三样：`.order_by(Task.id.desc())` 新的排前面，`.limit(limit)` 最多取几条，`total` 数一共几条。

### 增：POST /tasks

```python
# app/main.py（接着写）
@app.post("/tasks", status_code=201)                # 新建成功返回 201
def create_task(body: TaskCreate, session: Db) -> dict:   # body：请求体 {"title": ..., "note": ...}，先按 TaskCreate 校验
    if session.scalar(select(Task).where(Task.title == body.title, Task.done.is_(False))):   # SELECT * FROM tasks WHERE title = '写笔记' AND done IS false，查到一条就算重名
        raise fail(409, "已经有一条同名的未完成任务")   # 重名就报 409，下面不会执行
    task = Task(title=body.title, note=body.note)    # 在内存里建一个 Task 对象，还没进数据库
    session.add(task)                                # 记下「要插入」，下一行 commit 才发 INSERT
    session.commit()                                 # INSERT INTO tasks ...，真正写进数据库；提交失败就报错，不会被当成成功
    return success(TaskOut.model_validate(task), msg="创建成功")   # Task → TaskOut，返回 {code, msg, data: {id, title, ...}}
```

- 参数从第 3.8 节的 `?title=...` 换成了请求体 `body: TaskCreate`（第 3.3 节），标题长度这些校验交给 pydantic。
- 只拦「同名的**未完成**任务」：已经完成的同名任务不算冲突。`.where(条件1, 条件2)` 是「且」。
- **`Task.done.is_(False)`**：生成 SQL 的 `done IS false`。写成 `Task.done == False` 也能用，只是代码检查工具会提示「别用 == 和 False 比较」。

### 查一条：GET /tasks/1

```python
# app/main.py（接着写）
@app.get("/tasks/{task_id}")                        # {task_id} 是路径参数：/tasks/1 → task_id = 1
def get_task(task_id: int, session: Db) -> dict:
    return success(TaskOut.model_validate(load_task(session, task_id)))   # 查一条 → 转成 TaskOut → 包成 {code, msg, data}
```

查不到时 `load_task` 里直接抛 404，这里不用再判断。

### 改：PATCH /tasks/1/done

```python
# app/main.py（接着写）
@app.patch("/tasks/{task_id}/done")                 # PATCH：只改一部分字段
def finish_task(task_id: int, session: Db) -> dict:
    task = load_task(session, task_id)               # 先查出来，查不到就 404
    task.done = True                                 # 改属性就行，这时还没写进数据库
    session.commit()                                 # UPDATE tasks SET done = true, updated_at = ... WHERE id = 1
    return success(TaskOut.model_validate(task))     # 返回改完的任务，done 已经是 true
```

### 删：DELETE /tasks/1

```python
# app/main.py（接着写）
# 删除成功返回 200 而不是 204：204 表示「没有响应体」，而我们约定每个响应都有 {code, msg, data}
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Db) -> dict:
    session.delete(load_task(session, task_id))      # 先 SELECT 查出来（查不到就 404），再记下「要删除」
    session.commit()                                 # DELETE FROM tasks WHERE id = 1
    return success(msg="删除成功")                    # data 是 null：删掉的东西不用再返回
```

### 启动试一下

启动：`uvicorn app.main:app --reload`，到 `/docs` 里点着试，或者用 curl：

```bash
curl -X POST http://127.0.0.1:8000/tasks -H 'Content-Type: application/json' -d '{"title": "写笔记"}'
curl http://127.0.0.1:8000/tasks
curl -X PATCH http://127.0.0.1:8000/tasks/1/done
curl -i http://127.0.0.1:8000/tasks/99      # -i 显示状态码：404 + {"code": -1, "msg": "没有这个任务", "data": null}
```

## 3.11 写测试：pytest {#pytest}

`TestClient` 不用启动服务，就能在代码里对 app 发请求。pytest 自动找 `test_` 开头的文件和函数来跑。

下面按「准备、fixture、五个测试」分块写，几块代码依次放进同一个文件 `tests/test_tasks.py`。

### 准备：导入、连测试库

```python
# tests/test_tasks.py
from __future__ import annotations

from collections.abc import Iterator

import pytest                                       # 测试框架
from fastapi.testclient import TestClient           # 不启动服务，直接在代码里给 app 发请求
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, db_session                 # db_session：要被换掉的那个依赖（第 3.9 节）
from app.main import app                            # 要测的 app（第 3.10 节）


# 测试专用的库，和开发用的 todo 库分开：测试会把它清空
TEST_DATABASE_URL = "postgresql+psycopg://localhost:5432/todo_test"
engine = create_engine(TEST_DATABASE_URL)                                       # 连测试库
TestSession = sessionmaker(engine, autoflush=False, expire_on_commit=False)    # 测试库的会话工厂，参数和 db.py 里一样
```

**测试库一定要和开发库分开**：每个测试开始都会删表，要是连的是 `todo`，自己在 `/docs` 里建的数据就全没了。`todo_test` 是第 3.6 节末尾建好的。

### fixture：每个测试前准备好 client

```python
# tests/test_tasks.py（接着写）
@pytest.fixture                                     # 标记成 fixture：测试函数参数里写 client，pytest 就先跑它
def client() -> Iterator[TestClient]:
    # 每个测试开始前删表、重建：上一个测试留下的数据清干净，测试之间互不影响
    Base.metadata.drop_all(engine)                  # DROP TABLE tasks ...
    Base.metadata.create_all(engine)                # CREATE TABLE tasks ...

    def test_db_session() -> Iterator[Session]:     # 测试版的 db_session：连的是测试库
        session = TestSession()
        try:
            yield session                           # 交给接口用
            session.commit()                        # 接口正常返回后提交：INSERT / UPDATE / DELETE 这时才写进测试库
        finally:
            session.close()                         # 不管怎样都关闭

    app.dependency_overrides[db_session] = test_db_session   # 把真库换成测试库：接口要 db_session 时，改调 test_db_session
    with TestClient(app) as c:                      # with：启动、关闭 app（会执行 app 的启动代码）
        yield c                                     # 把 client 交给测试函数，测试跑完再回到这里
    app.dependency_overrides.clear()                # 收尾：撤掉替换，不影响别的地方
```

- **`@pytest.fixture`**：测试的准备工作。测试函数参数里写了 `client`，pytest 就先跑同名的 fixture，把 `yield` 出来的东西传进去；测试结束后执行 `yield` 后面的收尾。
- **`app.dependency_overrides`**：测试时把某个依赖换掉，这里把开发用的 `todo` 库换成测试专用的 `todo_test` 库。接口代码一行不用改。
- **为什么在测试开始前删表，而不是结束后**：测试失败时，数据还留在 `todo_test` 里，可以去 DBeaver 打开看是什么样。

### 测试一：新建后能在列表里看到

```python
# tests/test_tasks.py（接着写）
def test_create_and_list(client: TestClient) -> None:   # 参数 client：pytest 自动传入上面 fixture yield 出来的 c
    r = client.post("/tasks", json={"title": "写笔记"})   # 发 POST /tasks，json= 就是请求体
    assert r.status_code == 201                     # HTTP 状态码：新建成功是 201
    assert r.json()["code"] == 200                  # 响应体里的 code
    assert r.json()["data"]["title"] == "写笔记"
    assert r.json()["data"]["done"] is False        # 新建的任务默认没完成

    r = client.get("/tasks")                        # 再查列表
    assert r.status_code == 200
    assert r.json()["data"]["total"] == 1           # 一共 1 条
    assert [t["title"] for t in r.json()["data"]["items"]] == ["写笔记"]   # 取出所有标题，应该只有「写笔记」
```

**`assert 条件`**：条件不成立就算失败，pytest 会把两边的实际值打印出来。一个测试里可以写很多个 `assert`，遇到第一个失败的就停。

### 测试二：标题为空返回 422

```python
# tests/test_tasks.py（接着写）
def test_empty_title_rejected(client: TestClient) -> None:
    r = client.post("/tasks", json={"title": ""})   # 空标题：TaskCreate 要求至少 1 个字符
    assert r.status_code == 422                     # pydantic 校验不通过，接口函数根本不会执行
```

### 测试三：同名未完成任务返回 409

```python
# tests/test_tasks.py（接着写）
def test_duplicate_title_conflict(client: TestClient) -> None:
    client.post("/tasks", json={"title": "写笔记"})   # 先建一条
    r = client.post("/tasks", json={"title": "写笔记"})   # 再建同名的
    assert r.status_code == 409
    assert r.json() == {"code": -1, "msg": "已经有一条同名的未完成任务", "data": None}   # 整个响应体都对上，JSON 的 null 在 Python 里是 None
```

### 测试四：标记完成后按 done 筛选

```python
# tests/test_tasks.py（接着写）
def test_finish_and_filter(client: TestClient) -> None:
    a = client.post("/tasks", json={"title": "a"}).json()["data"]["id"]   # 建任务 a，记下它的 id
    client.post("/tasks", json={"title": "b"})      # 再建任务 b
    assert client.patch(f"/tasks/{a}/done").json()["data"]["done"] is True   # 把 a 标记完成，返回的 done 应该是 true
    items = client.get("/tasks", params={"done": False}).json()["data"]["items"]   # params= 拼成 ?done=false，只查没完成的
    assert [t["title"] for t in items] == ["b"]     # 只剩 b
```

### 测试五：删除后再查是 404

```python
# tests/test_tasks.py（接着写）
def test_delete_then_404(client: TestClient) -> None:
    task_id = client.post("/tasks", json={"title": "a"}).json()["data"]["id"]   # 先建一条，拿到 id
    r = client.delete(f"/tasks/{task_id}")          # 删掉它
    assert r.status_code == 200
    assert r.json()["msg"] == "删除成功"
    r = client.get(f"/tasks/{task_id}")             # 再查同一个 id
    assert r.status_code == 404                     # 已经没有了
    assert r.json() == {"code": -1, "msg": "没有这个任务", "data": None}
```

### 跑测试

在 `todo-api/` 目录运行：

```bash
python -m pytest -q            # 应该看到 5 passed
python -m pytest -q -k 404     # 只跑名字里带 404 的测试
```

## 3.12 拆文件和配置 {#routers-settings}

到 3.11 为止，所有接口都写在 `main.py` 里。接下来要加注册登录，接口会越来越多，先把结构理顺：**按业务拆成多个路由文件，配置集中到一个地方**。这一节只搬代码、不改功能，搬完 3.11 的测试应该原样通过。

先装一个新包，下面「配置」那部分要用（在 `todo-api/` 目录、激活了 `.venv` 的终端里执行）：

```bash
uv pip install pydantic-settings   # 用写 pydantic 模型的方式读配置（环境变量、.env）
```

拆完的目录（后面几节在这个基础上加文件）：

```
todo-api/
├── app/
│   ├── config.py          # 新增：所有配置
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── response.py
│   ├── errors.py
│   ├── routers/           # 新增：按业务分的接口
│   │   ├── __init__.py
│   │   └── tasks.py       # /tasks 相关的接口
│   └── main.py            # 只负责创建 app、把路由挂上去
└── tests/
```

### 配置：pydantic-settings

3.7 节用 `load_dotenv()` + `os.environ.get(...)` 读配置。配置一多就有问题：读出来全是字符串，要自己转类型；同一个配置在好几个文件里各读一遍，默认值还可能写得不一样。

`pydantic-settings` 用写 pydantic 模型的方式定义配置：字段名就是环境变量名，类型自动转换、校验，不对就启动失败。

```python
# app/config.py（新建）
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):                 # 继承 BaseSettings：字段从环境变量读
    """所有配置都在这里：先读环境变量，没有再读 .env，都没有用默认值。"""

    # 这个类自己的设置，两项：
    #   env_file=".env"：除了环境变量，还去读 .env 文件里的配置
    #   extra="ignore"：.env 里写了、但下面没定义成字段的项，直接跳过
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://localhost:5432/todo"   # 对应环境变量 DATABASE_URL（不区分大小写）
    debug: bool = False                       # DEBUG=true 会自动转成 True


settings = Settings()   # 整个项目共用这一个，别处 from app.config import settings
```

对应的 `.env`（3.7 节已经建过，在 `todo-api/` 下）：

```
# .env：自己电脑上真正用的配置，不提交
DATABASE_URL=postgresql+psycopg://localhost:5432/todo   # 对应 database_url
DEBUG=true                                               # 对应 debug；本地开着，能看到每条 SQL
```

`.env.example` 也同步加上 `DEBUG=false` 这一行，别人才知道有这个配置可以开。

- **字段名和环境变量名怎么对应**：`database_url` 对应 `DATABASE_URL`，不区分大小写，习惯上环境变量写大写。
- **不写也能跑**：`.env` 里没写的配置用代码里的默认值，比如不写 `DEBUG` 就是 `False`。
- **读取顺序**：环境变量 → `.env` 文件 → 默认值。线上直接设环境变量，本地写 `.env`，代码不用改，和 3.7 节一样。
- **自动转类型**：`DEBUG=true` 读进来就是 `True`，写成 `DEBUG=abc` 启动直接报错，不会带着错误的配置跑起来。
- **`extra="ignore"`**：`Settings` 只定义了 `database_url` 和 `debug` 两个字段。如果 `.env` 里还写了别的，比如 `SECRET_KEY=abc`，类里没有 `secret_key` 字段，这一行就直接跳过。不加 `extra="ignore"` 的话，默认会启动报错 `Extra inputs are not permitted`（不允许多余的配置）。

`app/db.py` 开头改成从 `settings` 读，`load_dotenv` 和 `os` 都不用了：

```python
# app/db.py（开头改成这样，后面不变）
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings              # 不用再 load_dotenv、os.environ.get

engine = create_engine(settings.database_url, echo=settings.debug)   # debug 时打印每条 SQL
```

### 拆路由：APIRouter

`APIRouter` 是「一组接口」，写法和 `app` 一样（`@router.get`、`@router.post`），最后挂到 `app` 上。把 3.10 节 `main.py` 里的接口整个搬过来，`@app` 换成 `@router`，路径去掉 `/tasks` 前缀。接口内容和 3.10 节一模一样，注释只标出变了的地方。

**`app/routers/tasks.py` 开头：建 router、搬 load_task**

```python
# app/routers/tasks.py（新建）
from __future__ import annotations

from fastapi import APIRouter                  # 用 APIRouter 代替 FastAPI
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import Db
from app.errors import fail, task_not_found
from app.models import Task
from app.response import success
from app.schemas import TaskCreate, TaskList, TaskOut

router = APIRouter(prefix="/tasks", tags=["任务"])   # prefix：路径都自动加上 /tasks；tags：/docs 里按这个分组


def load_task(session: Session, task_id: int) -> Task:   # 从 main.py 原样搬过来
    task = session.get(Task, task_id)          # SELECT * FROM tasks WHERE id = 1，按主键查一条
    if task is None:
        raise task_not_found()                 # 查不到就 404
    return task
```

**查：列表和详情**

```python
# app/routers/tasks.py（接着写）
@router.get("")                                # @app 换成 @router；完整路径 = prefix + "" = /tasks
def list_tasks(session: Db, done: bool | None = None, limit: int = 20) -> dict:
    stmt = select(Task).order_by(Task.id.desc()).limit(limit)   # SELECT * FROM tasks ORDER BY id DESC LIMIT 20
    if done is not None:
        stmt = stmt.where(Task.done == done)   # 传了 done 才加 WHERE done = ...
    tasks = session.scalars(stmt).all()        # 这时才执行上面拼好的 SELECT
    total = session.scalar(select(func.count()).select_from(Task))   # SELECT count(*) FROM tasks
    items = [TaskOut.model_validate(t) for t in tasks]   # Task → TaskOut
    return success(TaskList(items=items, total=total or 0))


@router.get("/{task_id}")                      # 完整路径 = /tasks/{task_id}
def get_task(task_id: int, session: Db) -> dict:
    return success(TaskOut.model_validate(load_task(session, task_id)))
```

**增、改、删**

```python
# app/routers/tasks.py（接着写）
@router.post("", status_code=201)              # POST /tasks
def create_task(body: TaskCreate, session: Db) -> dict:
    if session.scalar(select(Task).where(Task.title == body.title, Task.done.is_(False))):   # SELECT * FROM tasks WHERE title = '写笔记' AND done IS false：有同名的未完成任务
        raise fail(409, "已经有一条同名的未完成任务")
    task = Task(title=body.title, note=body.note)
    session.add(task)                                # 记下「要插入」
    session.commit()                           # INSERT INTO tasks (title, note, ...) VALUES (...)
    return success(TaskOut.model_validate(task), msg="创建成功")


@router.patch("/{task_id}/done")               # PATCH /tasks/{task_id}/done
def finish_task(task_id: int, session: Db) -> dict:
    task = load_task(session, task_id)
    task.done = True
    session.commit()                           # UPDATE tasks SET done = true, updated_at = ... WHERE id = 1
    return success(TaskOut.model_validate(task))


@router.delete("/{task_id}")                   # DELETE /tasks/{task_id}
def delete_task(task_id: int, session: Db) -> dict:
    session.delete(load_task(session, task_id))      # 先 SELECT 查出来（查不到就 404），再记下「要删除」
    session.commit()                           # DELETE FROM tasks WHERE id = 1
    return success(msg="删除成功")
```

**`app/main.py`：只剩创建 app、挂路由**

```python
# app/main.py（整个换成这样）
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import errors
from app.db import Base, engine
from app.routers import tasks                  # 导入 routers/tasks.py 这个模块


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:   # 服务启动、关闭时执行（第 2.8 节）
    Base.metadata.create_all(engine)   # 启动时建表（第 3.15 节换成 alembic）；不写在模块顶层，测试导入 app 时就不会去连真数据库
    yield                              # yield 之前：启动时跑；之后：关闭时跑（这里没有）


app = FastAPI(title="todo-api", lifespan=lifespan)   # 把 lifespan 交给 app
errors.install(app)                    # 登记错误处理器
app.include_router(tasks.router)       # 把路由挂到 app 上，不挂就是 404
```

拆完还差两步：给新建的 `routers/` 文件夹补一个 `__init__.py`，再跑一遍测试，确认搬完功能没变。

```bash
touch app/routers/__init__.py      # 新建一个空文件，标记 routers/ 是个包，和 3.1 节的 app/、tests/ 一样
python -m pytest -q                 # 跑 3.11 节的测试：还是 5 passed，说明只是搬了位置，功能没变
```

- **`__init__.py`**：空文件，只起标记作用，`main.py` 里的 `from app.routers import tasks` 就是从这个包里导入。严格说 Python 3.3 以后没有它也能 import，但 pytest 这类工具在有它时更稳定，项目里习惯都放。
- **跑测试**：不用去 `/docs` 里一个个点。要是看到 `failed`，比如忘了 `include_router`，接口会变成 404，测试会直接指出是哪个测试、哪一行出错。

以后再加一类业务（比如「标签」），就是新建 `routers/tags.py`，在 `main.py` 里多一行 `include_router`。

## 3.13 注册登录：JWT {#auth}

现在谁都能调接口，所有人看到的也是同一份任务。要把每个人的数据分开，后端得先知道每个请求是谁发的。这一节加上账号：注册、登录，登录成功后后端发一个 **token**（身份凭证：里面写着用户 id，后端签过名，改不了）。之后每次请求带上它，后端验过签名就知道「你是谁」，这一步叫**认证**。知道是谁之后，才能判断「你能不能做这件事」，这叫**权限**。下一节让每个人只能看、改自己的任务，就是最简单的权限。

先装两个新包：

```bash
uv pip install pyjwt "pwdlib[argon2]"   # pyjwt：生成、校验 token；pwdlib[argon2]：给密码算哈希
```

### 几种登录方式

先分清两件事：**登录状态存在哪里**和**凭证怎么带到后端**，它们是分开选的。

**登录状态存在哪里**

| | Session（后端存会话） | JWT（这一节用的） |
|---|---|---|
| 登录后后端存什么 | 在数据库 / Redis 里存一条会话，发给前端一个随机的会话 id | 什么都不存，把用户 id、过期时间写进 token 并签名 |
| 之后怎么认人 | 拿会话 id 去查那条会话 | 验签名，签名对就直接读出用户 id，不查库 |
| 退出登录 / 踢人下线 | 删掉那条会话，立刻生效 | token 在过期前一直有效，要做黑名单才能提前作废 |
| 多个服务之间 | 每个服务都要能查同一份会话存储 | 每个服务有密钥就能自己验 |

**凭证怎么带到后端**（上面两种都可以用这两种带法）

| | Cookie | 请求头 `Authorization: Bearer <xxx>` |
|---|---|---|
| 谁来带 | 浏览器自动带 | 前端代码自己存、自己加 |
| 要注意 | 要防 CSRF；设 `HttpOnly` 后 JS 读不到，能防 XSS 偷走 | 存在 localStorage 里时，页面有 XSS 就可能被读走 |
| 跨域 / App | 跨域要额外配置，App 和小程序用起来麻烦 | 不受限制，App、小程序、服务之间调用都方便 |

这一节用 **JWT + 请求头**，因为前后端分开部署时这种组合最省事。代价是 token 不好提前作废，所以过期时间不要设太长。

**JWT 长什么样**：三段，用 `.` 连起来。拆开看：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9         头部：{"alg":"HS256","typ":"JWT"}  用什么算法
eyJzdWIiOiIxIiwiZXhwIjoxNzk1MDg5Mzc1fQ       内容：{"sub":"1","exp":1795089375}  用户 id、过期时间
psp76-RKMAF2K4GSPyTENws3zIN6Fu5trWmGusoO1Rg  签名
```

- 前两段只是 base64 编码，**不是加密**，谁都能解开看到内容。所以里面只放用户 id，不放密码、手机号这类信息。
- 第三段是用 `jwt_secret` 对前两段算出来的签名。别人改了内容（比如把 `sub` 改成别人的 id），签名就对不上，`jwt.decode` 会报错。所以**密钥一定不能泄露**，泄露了谁都能伪造任意用户的 token。

### 密码：只存哈希

数据库里绝不能存明文密码。存的是**哈希**：一种单向的计算，`hash_password("123456")` 能算出一长串，但从这一长串反推不出 `123456`。登录时把用户输入的密码再算一遍、比一比就行。

```python
hash_password("123456")
# $argon2id$v=19$m=65536,t=3,p=4$+1qkfLNB9eexyrW0v6KHPA$WSSmXl1va571FXD0LjyeIJ1cgD4jfUueruDahstIvIk
#  算法     参数               盐（随机）              哈希值
```

同一个密码，每次算出来的结果都不一样：里面混了一段随机的「盐」，存在结果里，验证时取出来用。这样两个用户都用 `123456`，存的也不一样，别人没法拿一张「常见密码 → 哈希」的表去对。**别自己用 md5、sha256 算**：它们太快了，被拖库后能被暴力猜出来。Argon2 是专门为存密码设计的，故意算得慢。

### 代码

`app/config.py` 加两个配置：

```python
    # app/config.py（Settings 类里加上这两行）
    jwt_secret: str = "dev-secret-change-me"  # 签 token 的密钥，线上一定要换成随机长字符串
    token_days: int = 7                       # token 几天后过期
```

生成一个随机密钥写进 `.env`：`python -c "import secrets; print(secrets.token_urlsafe(32))"`。

```
# .env（加上这两行）
JWT_SECRET=把上面命令打印出来的那串粘贴到这里    # 对应 jwt_secret
TOKEN_DAYS=7                                     # 对应 token_days，不写就用默认的 7
```

`.env.example` 里写成 `JWT_SECRET=换成你自己的随机字符串`，不要把真实密钥提交上去。

`app/models.py` 加一张用户表：

```python
# app/models.py（加一个 User 类）
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)   # unique：不能重名
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)          # 只存哈希，不存密码
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
```

`app/schemas.py` 加注册登录的请求体和返回格式：

```python
# app/schemas.py（末尾加上）
class AuthIn(BaseModel):
    """注册、登录的请求体。"""
    username: str = Field(min_length=2, max_length=20, pattern=r"^\w+$")   # 2～20 个字；\w 是字母、数字、下划线、汉字
    password: str = Field(min_length=6, max_length=128)                    # 至少 6 位


class TokenOut(BaseModel):                     # 注册、登录成功后返回的 data
    token: str                                 # 前端存起来，之后每次请求带上
    username: str                              # 页面上显示用
```

密码和 token 的处理单独放一个文件 `app/security.py`，分三块写。

**开头和密码：只存哈希**

```python
# app/security.py（新建）
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt                                     # pyjwt：生成、校验 token
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer   # 从请求头取 Bearer token
from pwdlib import PasswordHash                # 密码哈希

from app.config import settings
from app.db import Db
from app.errors import fail
from app.models import User

password_hash = PasswordHash.recommended()     # 用 Argon2 算法


def hash_password(password: str) -> str:       # 注册时用：明文 → 哈希，存进数据库
    return password_hash.hash(password)        # 每次结果都不一样：里面带了随机的盐


def verify_password(password: str, hashed: str) -> bool:   # 登录时用：输入的密码和存的哈希对不对得上
    return password_hash.verify(password, hashed)
```

**token：登录后发给前端，之后每次请求带上**

```python
# app/security.py（接着写）
def create_token(user_id: int) -> str:
    payload = {                                # token 里放的内容（谁都能解开看，只放 id）
        "sub": str(user_id),                                            # 这个 token 属于谁
        "exp": datetime.now(UTC) + timedelta(days=settings.token_days),  # 过期时间，过期后 decode 会报错
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")   # 用密钥签名，得到 eyJ... 这样的字符串
```

**current_user：从请求头认出当前用户**

```python
# app/security.py（接着写）
bearer = HTTPBearer(auto_error=False)          # auto_error=False：没带 token 时不让 FastAPI 自己报 403，交给下面统一返回 401


def current_user(
    session: Db,                               # 依赖里还能再用依赖：拿数据库会话
    cred: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],   # 请求头里的 token，没带就是 None
) -> User:
    """依赖：从请求头 Authorization: Bearer <token> 解析出当前用户，不对就 401。"""
    if cred is None:                           # 没带 token
        raise fail(401, "请先登录")
    try:
        payload = jwt.decode(cred.credentials, settings.jwt_secret, algorithms=["HS256"])   # 验签名、验过期，通过才拿到内容
    except jwt.ExpiredSignatureError:          # 过期了
        raise fail(401, "登录已过期，请重新登录") from None
    except jwt.InvalidTokenError:              # 被改过、格式不对
        raise fail(401, "登录无效，请重新登录") from None
    user = session.get(User, int(payload["sub"]))   # SELECT * FROM users WHERE id = ...
    if user is None:                                   # token 是对的，但用户已经被删了
        raise fail(401, "账号不存在，请重新登录")
    return user                                # 接口里的 user 参数拿到的就是它


CurrentUser = Annotated[User, Depends(current_user)]   # 接口里写 user: CurrentUser 就要求登录
```

- **`current_user` 是一个依赖**：和 3.9 节的 `db_session` 一样，接口参数写 `user: CurrentUser`，FastAPI 就先执行它。没带 token、token 被改过、过期了，都会 `raise fail(401, ...)`，接口函数根本不会执行。它自己也依赖 `Db`，依赖可以一层套一层。
- **`HTTPBearer`**：FastAPI 自带的，负责从请求头 `Authorization: Bearer xxx` 里取出 `xxx`。用它还有个好处：`/docs` 右上角会出现 **Authorize** 按钮，填一次 token，之后点着试的请求都会自动带上。
- **`raise ... from None`**：在 `except` 里抛新的错误时，不把原来那个 JWT 的报错串在后面，日志干净一些。

注册、登录接口放在 `app/routers/auth.py`：

**开头**

```python
# app/routers/auth.py（新建）
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.db import Db
from app.errors import fail
from app.models import User
from app.response import success
from app.schemas import AuthIn, TokenOut
from app.security import CurrentUser, create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["账号"])   # 路径都以 /auth 开头，/docs 里归到「账号」
```

**注册：POST /auth/register**

```python
# app/routers/auth.py（接着写）
@router.post("/register", status_code=201)
def register(body: AuthIn, session: Db) -> dict:
    if session.scalar(select(User).where(User.username == body.username)):   # SELECT ... WHERE username = 'tom'，已经有了
        raise fail(409, "这个用户名已经被注册了")
    user = User(username=body.username, password_hash=hash_password(body.password))   # 存哈希，不存明文
    session.add(user)                                # 记下「要插入」
    session.commit()                           # INSERT INTO users ...，之后 user.id 有值
    return success(TokenOut(token=create_token(user.id), username=user.username), msg="注册成功")   # 直接发 token，等于已经登录
```

- **注册成功直接返回 token**：等于注册完就登录了，前端不用再调一次登录接口。

**登录：POST /auth/login**

```python
# app/routers/auth.py（接着写）
@router.post("/login")
def login(body: AuthIn, session: Db) -> dict:
    user = session.scalar(select(User).where(User.username == body.username))   # SELECT * FROM users WHERE username = 'tom'，查不到是 None
    if user is None or not verify_password(body.password, user.password_hash):   # 用户不存在、密码错，都走这里
        raise fail(401, "用户名或密码错误")      # 两种情况同一句话：不告诉别人「这个用户名是存在的」
    return success(TokenOut(token=create_token(user.id), username=user.username), msg="登录成功")
```

- **登录失败只说「用户名或密码错误」**：如果分别提示「用户不存在」「密码错误」，别人就能一个个试出哪些用户名注册过。

**当前用户：GET /auth/me**

```python
# app/routers/auth.py（接着写）
@router.get("/me")
def me(user: CurrentUser) -> dict:           # 声明要 CurrentUser：没登录进不来
    return success({"id": user.id, "username": user.username})
```

`app/main.py` 里挂上新路由，改两处：

```python
# app/main.py（改这两处，其余不变）
from app.routers import auth, tasks            # 多导入一个 auth

app.include_router(auth.router)                # 新加：挂上 /auth/... 这几个接口，不挂就是 404
app.include_router(tasks.router)               # 原来就有
```

`users` 是一张新表，启动时 `create_all` 会自动建上，不用删库。

实际运行（curl）：

| 请求 | HTTP | 响应 |
|---|---|---|
| `POST /auth/register` `{"username":"tom","password":"123456"}` | 201 | `{"code":200,"msg":"注册成功","data":{"token":"eyJ...","username":"tom"}}` |
| `GET /auth/me`，带 `Authorization: Bearer eyJ...` | 200 | `{"code":200,"msg":"ok","data":{"id":1,"username":"tom"}}` |
| `GET /auth/me`，不带 token | 401 | `{"code":-1,"msg":"请先登录","data":null}` |
| `POST /auth/login`，密码错 | 401 | `{"code":-1,"msg":"用户名或密码错误","data":null}` |
| `POST /auth/register`，用户名已存在 | 409 | `{"code":-1,"msg":"这个用户名已经被注册了","data":null}` |

### 对比：用中间件做鉴权（了解即可）

不用依赖、改用中间件（3.16 节细讲）也能做登录检查，有的项目会这么写。FastAPI 里主流是上面的依赖注入，这段只用来对比，**不用写进项目**：

```python
# app/main.py（只做对比，项目里不这样写）
import jwt
from fastapi import Request
from fastapi.responses import JSONResponse

PUBLIC_PATHS = {"/auth/register", "/auth/login", "/docs", "/openapi.json"}   # 白名单：这些路径不要求登录；新加公开接口忘了加进来，就会被拦住


@app.middleware("http")                        # 每个请求都会先进这个函数，不管是哪个接口
async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:       # 公开接口直接放行
        return await call_next(request)

    auth = request.headers.get("Authorization", "")   # 自己从请求头取 token（依赖写法里是 HTTPBearer 取的）
    if not auth.startswith("Bearer "):
        # 不能 raise fail(...)：中间件在异常处理器外层，抛出去没人接，会变成 500
        # 只能自己拼统一格式返回
        return JSONResponse({"code": -1, "msg": "请先登录", "data": None}, status_code=401)
    try:
        payload = jwt.decode(auth.removeprefix("Bearer "), settings.jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:              # 过期（ExpiredSignatureError）也是它的子类，一起接住
        return JSONResponse({"code": -1, "msg": "登录无效，请重新登录", "data": None}, status_code=401)

    request.state.user_id = int(payload["sub"])   # 结果没法当参数传给接口，只能挂在 request.state 上
    return await call_next(request)            # 放行，去执行接口


@app.get("/auth/me")
def me(request: Request, session: Db) -> dict:   # 要多写一个 request 参数
    user = session.get(User, request.state.user_id)   # SELECT * FROM users WHERE id = 1；自己取出 id、自己查用户，request.state 没有类型，编辑器不提示
    return success({"id": user.id, "username": user.username})
```

实际运行：不带 token、带假 token 都返回 401，带对的 token 返回 200，`/auth/login`、`/docs` 不带也能访问；在中间件里改成 `raise fail(401, "请先登录")`，返回的是 `500 Internal Server Error`。

和依赖写法比，要多管白名单、自己拼报错格式、接口里自己取用户。所以 FastAPI 里鉴权用依赖，中间件留给记日志、算耗时这类每个请求都要做、接口不需要结果的事。

## 3.14 一对多和分页 {#relations-paging}

能登录了，但任务还是所有人共用一份。这一节给任务加上「属于谁」，每个接口只操作自己的任务；顺便把列表改成分页。

### 一对多：外键和 relationship

一个用户有多条任务，一条任务只属于一个用户，这叫**一对多**。做法是在「多」的那一边（`tasks` 表）加一列 `user_id`，存它属于哪个用户：

```
users                    tasks
id | username            id | user_id | title
 1 | tom          ←──────  1 |    1    | 写笔记
 2 | jerry        ←──┐     2 |    1    | 读书
                     └───  3 |    2    | 跑步
```

```python
# app/models.py（改动的部分）
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    ...                                                               # 原来的字段不变
    tasks: Mapped[list[Task]] = relationship(back_populates="user", cascade="all, delete-orphan")   # 用户 → 他的所有任务（不是表里的列）


class Task(Base):
    ...                                                               # 原来的字段不变
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)   # 外键：属于哪个用户；加索引，按用户查更快
    ...
    user: Mapped[User] = relationship(back_populates="tasks")          # 反过来：任务 → 用户
```

- **`ForeignKey("users.id")`**：外键。数据库会检查 `user_id` 必须是 `users` 表里真实存在的 id，不能随便填。
- **`index=True`**：给这一列建**索引**。没有索引时，按 `user_id` 查要把整张表从头扫到尾；有了索引，就像书的目录，直接翻到那几行。经常出现在 `where` 里的列都应该加索引。
- **`relationship`**：不对应数据库里的列，是 SQLAlchemy 提供的便利：`tom.tasks` 拿到他的所有任务，`task.user` 拿到任务的主人，它自己去查。`back_populates` 把两边连起来，改一边另一边也同步。
- **`cascade="all, delete-orphan"`**：删用户时，他的任务一起删掉。

```python
tom = User(username="tom", password_hash="...")
tom.tasks.append(Task(title="写笔记"))     # 不用自己填 user_id
tom.tasks.append(Task(title="读书"))
session.add(tom)                                     # 记下「要插入」：tom 和他的两条任务
session.commit()                                     # INSERT INTO users ...，再 INSERT INTO tasks 两条，user_id 自动填 tom 的 id

print([t.title for t in tom.tasks])       # ['写笔记', '读书']
print(session.get(Task, 1).user.username) # tom：先 SELECT * FROM tasks WHERE id = 1，访问 .user 时再 SELECT * FROM users WHERE id = 1
session.delete(tom)                       # 删 tom，他的两条任务也跟着删（cascade）：commit 时先 DELETE 两条 tasks，再 DELETE FROM users WHERE id = 1
```

`relationship` 适合「拿一个对象顺带看看关联的东西」。要按条件筛选、分页、计数，还是自己写 `select(...).where(...)`，下面的接口就是这样做的。

> **多对多**（比如任务和标签：一个任务多个标签，一个标签多个任务）要再建一张中间表，只存 `task_id` 和 `tag_id` 两列。原理一样，用到再查文档。

### 接口：加上「是不是自己的」

`schemas.py` 里 `TaskList` 加两个字段，告诉前端现在是第几页：

```python
# app/schemas.py（TaskList 改成这样）
class TaskList(BaseModel):
    items: list[TaskOut]      # 模型可以嵌套
    total: int                # 符合条件的一共多少条（不是这一页的条数）
    page: int                 # 当前第几页
    size: int                 # 每页几条
```

`app/routers/tasks.py` 改成下面这样，分四块。

**开头：load_task 多传一个 user**

```python
# app/routers/tasks.py（整个换成这样）
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query           # Query：给查询参数加校验（分页用）
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import Db
from app.errors import fail, task_not_found
from app.models import Task, User
from app.response import success
from app.schemas import TaskCreate, TaskList, TaskOut
from app.security import CurrentUser           # 要求登录（第 3.13 节）

router = APIRouter(prefix="/tasks", tags=["任务"])


def load_task(session: Session, task_id: int, user: User) -> Task:
    """取自己的一条任务。别人的任务也当成不存在：返回 404，不告诉对方「有这条，但不是你的」。"""
    task = session.get(Task, task_id)          # SELECT * FROM tasks WHERE id = ...
    if task is None or task.user_id != user.id:   # 不存在，或者不是自己的
        raise task_not_found()                 # 都返回 404
    return task
```

**查列表：只查自己的，带分页**

```python
# app/routers/tasks.py（接着写）
@router.get("")
def list_tasks(
    user: CurrentUser,                                   # 当前登录的用户，没登录就 401
    session: Db,
    done: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,              # 第几页，从 1 开始
    size: Annotated[int, Query(ge=1, le=100)] = 20,     # 每页几条，最多 100，防止一次拉太多
) -> dict:
    conditions = [Task.user_id == user.id]               # 只查自己的：WHERE user_id = 1
    if done is not None:
        conditions.append(Task.done == done)             # 再加 AND done = ...

    total = session.scalar(select(func.count()).select_from(Task).where(*conditions))   # SELECT count(*) FROM tasks WHERE user_id = 1 AND done = false：和下面列表同一组条件
    # 拼成一条 SQL（以 page=2、size=20、done=false 为例）：
    # SELECT * FROM tasks WHERE user_id = 1 AND done = false ORDER BY id DESC LIMIT 20 OFFSET 20
    stmt = (
        select(Task)                                     # SELECT * FROM tasks
        .where(*conditions)                              # WHERE user_id = 1 AND done = false：和上面 count 用同一组条件
        .order_by(Task.id.desc())                        # ORDER BY id DESC：新的排前面
        .offset((page - 1) * size)                       # OFFSET 20：跳过前面几页，(2 - 1) × 20 = 20 条
        .limit(size)                                     # LIMIT 20：这一页取几条
    )
    items = [TaskOut.model_validate(t) for t in session.scalars(stmt)]   # 这时才执行上面拼好的 SELECT，每条转成 TaskOut
    return success(TaskList(items=items, total=total or 0, page=page, size=size))
```

实际运行。tom 登录后建了三条：写笔记（已完成）、读书、跑步：

```
GET /tasks
Authorization: Bearer <tom 的 token>
```

```json
{
  "code": 200,
  "msg": "ok",
  "data": {
    "items": [
      {"id": 3, "title": "跑步", "done": false, "note": null, "created_at": "2026-11-20T16:21:04.497317+08:00", "updated_at": "2026-11-20T16:21:04.497318+08:00"},
      {"id": 2, "title": "读书", "done": false, "note": null, "created_at": "2026-11-20T16:21:04.487204+08:00", "updated_at": "2026-11-20T16:21:04.487206+08:00"},
      {"id": 1, "title": "写笔记", "done": true, "note": null, "created_at": "2026-11-20T16:21:04.474762+08:00", "updated_at": "2026-11-20T16:21:04.506914+08:00"}
    ],
    "total": 3,
    "page": 1,
    "size": 20
  }
}
```

其他几种请求（都带 tom 的 token，除非写了「不带」）：

| 请求 | HTTP | 响应 |
|---|---|---|
| `GET /tasks?done=false` | 200 | `items` 只有「跑步」「读书」，`"total":2,"page":1,"size":20` |
| `GET /tasks?page=2&size=2` | 200 | `items` 只有「写笔记」，`"total":3,"page":2,"size":2`：一共 3 条，每页 2 条，第 2 页只剩 1 条 |
| `GET /tasks`，不带 token | 401 | `{"code":-1,"msg":"请先登录","data":null}` |
| `GET /tasks?size=500` | 422 | `{"code":-1,"msg":"size：Input should be less than or equal to 100","data":null}` |

**增：同名只在自己的任务里查**

```python
# app/routers/tasks.py（接着写）
@router.post("", status_code=201)
def create_task(body: TaskCreate, user: CurrentUser, session: Db) -> dict:
    same = select(Task).where(Task.user_id == user.id, Task.title == body.title, Task.done.is_(False))   # SELECT * FROM tasks WHERE user_id = 1 AND title = '写笔记' AND done IS false：自己的、同名、未完成（只是拼好）
    if session.scalar(same):                         # 执行上面的 SELECT，查到一条就算重名
        raise fail(409, "已经有一条同名的未完成任务")
    task = Task(user_id=user.id, title=body.title, note=body.note)   # 新任务属于当前用户
    session.add(task)                                # 记下「要插入」
    session.commit()                                     # INSERT INTO tasks (user_id, title, note, ...) VALUES (1, '写周报', ...)
    return success(TaskOut.model_validate(task), msg="创建成功")
```

实际运行（jerry 是另一个已注册的用户）：

| 请求 | HTTP | 响应 |
|---|---|---|
| `POST /tasks`，tom，`{"title":"写周报","note":"周五前"}` | 201 | `{"code":200,"msg":"创建成功","data":{"id":4,"title":"写周报","done":false,"note":"周五前","created_at":"2026-11-20T08:21:04.552446Z","updated_at":"2026-11-20T08:21:04.552446Z"}}` |
| `POST /tasks`，tom，`{"title":"读书"}` | 409 | `{"code":-1,"msg":"已经有一条同名的未完成任务","data":null}` |
| `POST /tasks`，jerry，`{"title":"读书"}` | 201 | `{"code":200,"msg":"创建成功","data":{"id":5,"title":"读书",...}}`：别人的同名任务不算重名 |

**查一条、改、删：都走 load_task**

```python
# app/routers/tasks.py（接着写）
@router.get("/{task_id}")
def get_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    return success(TaskOut.model_validate(load_task(session, task_id, user)))   # 别人的任务也是 404


@router.patch("/{task_id}/done")
def finish_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    task = load_task(session, task_id, user)            # 先确认是自己的
    task.done = True
    session.commit()                                     # UPDATE tasks SET done = true, updated_at = ... WHERE id = 2
    return success(TaskOut.model_validate(task))


@router.delete("/{task_id}")
def delete_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    session.delete(load_task(session, task_id, user))   # 先确认是自己的（load_task 里 SELECT），再记下「要删除」
    session.commit()                                     # DELETE FROM tasks WHERE id = 3
    return success(msg="删除成功")
```

实际运行（任务 2「读书」、任务 3「跑步」都是 tom 的）：

| 请求 | HTTP | 响应 |
|---|---|---|
| `GET /tasks/2`，tom | 200 | `{"code":200,"msg":"ok","data":{"id":2,"title":"读书","done":false,"note":null,...}}` |
| `GET /tasks/2`，jerry | 404 | `{"code":-1,"msg":"没有这个任务","data":null}`：别人的任务当成不存在 |
| `PATCH /tasks/2/done`，tom | 200 | `{"code":200,"msg":"ok","data":{"id":2,"title":"读书","done":true,...}}` |
| `PATCH /tasks/2/done`，jerry | 404 | `{"code":-1,"msg":"没有这个任务","data":null}` |
| `DELETE /tasks/3`，jerry | 404 | `{"code":-1,"msg":"没有这个任务","data":null}` |
| `DELETE /tasks/3`，tom | 200 | `{"code":200,"msg":"删除成功","data":null}` |
| `GET /tasks/3`，tom，删完再查 | 404 | `{"code":-1,"msg":"没有这个任务","data":null}` |

- **每个接口都加了 `user: CurrentUser`**：不登录访问任何任务接口都是 401。
- **3.11 的测试会跟着失败**：那些测试没带 token，现在都会返回 401。要让它们继续通过，测试里先调 `/auth/register` 拿到 token，每个请求加上 `headers={"Authorization": f"Bearer {token}"}`。
- **列表**：条件里加 `Task.user_id == user.id`，只查自己的。
- **单条（详情、完成、删除）**：都走 `load_task`，查到了还要比一下 `task.user_id`。**不能只靠前端「不显示」**：别人直接改网址里的 id 就能访问，后端必须每次检查。返回 404 而不是 403，不暴露「这个 id 存在」。
- **同名检查**也只在自己的任务里查：你有「写笔记」，不影响别人也建一条「写笔记」。

### 分页

数据多了不能一次全返回。约定前端传 `page`（第几页）和 `size`（每页几条），后端换算成 SQL 的 `OFFSET` 和 `LIMIT`：

| page | size | offset = (page - 1) × size | 拿到的是 |
|---|---|---|---|
| 1 | 10 | 0 | 第 1～10 条 |
| 2 | 10 | 10 | 第 11～20 条 |
| 3 | 10 | 20 | 第 21～30 条 |

- **`Query(ge=1, le=100)`**：查询参数也能像 `Field` 一样加校验。`size` 不设上限的话，有人传 `size=1000000` 就能把数据库拖垮。
- **`total` 和列表用同一组条件**：前端靠 `total` 算总页数。3.10 节的 `total` 数的是整张表，没带 `done` 筛选，其实是个 bug；现在两条查询共用 `conditions`，不会再对不上。
- **一定要 `order_by`**：不排序的话，数据库不保证每次返回的顺序一样，翻页时可能有的数据重复出现、有的永远看不到。

> 页数很深（比如第 10000 页）时，`OFFSET` 会越来越慢，因为数据库要先数过前面所有行。那种场景用「游标分页」：前端传上一页最后一条的 id，后端查 `where id < 那个 id`。一般的后台列表用 `page / size` 就够了。

表结构又变了（`tasks` 加了 `user_id`），**再删一次库重建**：`dropdb todo && createdb todo`。这种「改一次表就删一次库」的做法到这里为止，下一节换成 alembic。

## 3.15 数据库迁移：Alembic {#alembic}

前面每次改表都要删库重建，因为 `create_all` 只会建不存在的表，不会改已有的表。自己练习时没问题，真实项目里有两个麻烦：

- **线上的数据不能删**：表结构要改，数据要留着。
- **多人开发时，每个人的库都要跟着改**：你加了一列，同事电脑上的库、线上的库也得加上。靠口头通知、各自手动改库，迟早会漏。

迁移工具同时解决这两件事：

- 每次改表，生成一个**迁移脚本**，写着「这次加了哪一列」「建了哪张表」。
- 数据库里多一张 `alembic_version` 表，记着当前执行到哪个版本。
- `alembic upgrade head` 把还没执行的脚本按顺序执行一遍。本地、同事电脑、线上，都用同一套脚本升到同一个结构。

迁移脚本要提交到 git，和代码一起走：同事拉下代码，跑一次 `alembic upgrade head` 就同步了，具体流程见下面的「多人协作」。

```bash
uv pip install alembic         # 装数据库迁移工具
alembic init migrations        # 在 todo-api/ 下生成 alembic.ini 和 migrations/ 目录
```

### 配置：改 `migrations/env.py` 的两处

生成的 `env.py` 不知道你的数据库在哪、表长什么样。找到 `target_metadata = None` 那一段，换成：

```python
# migrations/env.py（alembic init 生成的文件；把 target_metadata = None 那一段换成下面这些）

# ---- 改动 ①：数据库地址和项目用同一份配置，不在 alembic.ini 里再写一遍 ----
from app import models  # noqa: E402,F401  导入一下，表才会登记到 Base.metadata 上
from app.config import settings  # noqa: E402
from app.db import Base  # noqa: E402

config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))  # % 要写成 %%

# ---- 改动 ②：告诉 alembic「代码里的表长什么样」，autogenerate 拿它和数据库对比 ----
target_metadata = Base.metadata
```

`.replace("%", "%%")`：`alembic.ini` 的格式把 `%` 当特殊字符，数据库密码里有 `%` 时不转义会报错。

最后，`main.py` 里的 `lifespan` 和 `create_all` **删掉**：表结构从此只由 alembic 管。

原来（3.12 节写的，3.13 节加了 auth）：

```python
# app/main.py（原来）
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:   # 服务启动时执行
    Base.metadata.create_all(engine)   # 启动时按模型建表：只建不存在的表，不会改已有的表
    yield


app = FastAPI(title="todo-api", lifespan=lifespan)
errors.install(app)
app.include_router(auth.router)
app.include_router(tasks.router)
```

改成：

```python
# app/main.py（整个换成这样）
from __future__ import annotations

from fastapi import FastAPI

from app import errors
from app.routers import auth, tasks

app = FastAPI(title="todo-api")         # 不再 create_all：表结构交给 alembic
errors.install(app)
app.include_router(auth.router)
app.include_router(tasks.router)
```

`lifespan` 整个删掉，跟着没用的 `AsyncIterator`、`asynccontextmanager`、`Base`、`engine` 这几个导入也一起删。

测试里的 `drop_all` / `create_all` 留着：`todo_test` 每个测试都要清空重建，直接按模型建表最省事。

### 第一次：从现在的表结构生成迁移

```bash
dropdb todo && createdb todo                          # 最后一次删库：之后都靠迁移
alembic revision --autogenerate -m "create users and tasks"
alembic upgrade head
```

`--autogenerate` 会把代码里的表和数据库里的表做对比，把差别写成脚本，放在 `migrations/versions/` 下面：

```python
# migrations/versions/8b00b78b9f87_create_users_and_tasks.py（自动生成的，节选）
"""create users and tasks

Revision ID: 8b00b78b9f87
Revises:
"""
revision: str = '8b00b78b9f87'
down_revision: Union[str, Sequence[str], None] = None    # 上一个版本：第一个没有


def upgrade() -> None:                                    # 升级：执行这个
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    ...
    )
    op.create_table('tasks', ...)
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)   # user_id 的索引


def downgrade() -> None:                                  # 回退：执行这个，把 upgrade 做的撤销掉
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('users')
```

执行完，数据库里多了 `alembic_version` 表，记着当前版本 `8b00b78b9f87`。

### 之后每次改表：改模型 → 生成 → 检查 → 升级

比如给任务加一个优先级。先往数据库里随便建几条任务，再改模型：

```python
# app/models.py，Task 里加一列
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
```

```bash
alembic revision --autogenerate -m "add task priority"
alembic upgrade head
```

**报错了**：

```
sqlalchemy.exc.IntegrityError: (psycopg.errors.NotNullViolation) column "priority" of relation "tasks" contains null values
```

原因：`default=0` 是 **Python 这边**的默认值，只在 SQLAlchemy 插入新数据时生效，数据库根本不知道。表里已经有的那几行，新加的 `priority` 列填什么？数据库只能填 NULL，而这一列又规定了不能为 NULL。

报错后数据库还停在上一个版本（`alembic current` 还是 `8b00b78b9f87`）：Postgres 里加列、建表也在事务里执行，迁移中途失败会整个撤销，不会改到一半。

改成同时写 `server_default`：这是**数据库这边**的默认值，加列时已有的行会自动填上它。删掉刚才生成的那个迁移文件，重新生成：

```python
    # app/models.py（Task 里 priority 这一行改成这样）
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
```

```bash
rm migrations/versions/*_add_task_priority.py
alembic revision --autogenerate -m "add task priority"
alembic upgrade head            # Running upgrade 8b00b78b9f87 -> c6314163489a, add task priority
```

生成的脚本：

```python
# migrations/versions/c6314163489a_add_task_priority.py（重新生成的，节选）
def upgrade() -> None:
    op.add_column('tasks', sa.Column('priority', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('tasks', 'priority')
```

原来的数据都还在，`priority` 自动是 0。接口返回里也要带上它，`TaskOut` 加一行：

```python
    # app/schemas.py（TaskOut 里加一行）
    priority: int             # 之后返回的任务里都多一个 "priority": 0
```

**给已经有数据的表加「不能为空」的列，一定要给 `server_default`。** 这个坑本地发现不了（本地经常是空表），一上线就炸。

### 多人协作：以模型为准，靠迁移脚本同步

表结构的「源头」是 `models.py` 里的类。要改表，只改模型，再生成迁移脚本；不要去数据库里手动 `ALTER TABLE`，也不要把自己库的表结构导出来发给别人。

| 谁 | 做什么 |
|---|---|
| 改表的人（A） | 改模型 → `alembic revision --autogenerate` → 打开脚本检查 → 模型改动和迁移脚本**一起提交** |
| 其他同事（B） | `git pull` 拿到新脚本 → `alembic upgrade head`，本地库就和 A 的一样了 |
| 线上 | 部署前同样跑 `alembic upgrade head` |

- **为什么不能手动改库**：手动改的只有你自己的库有，同事和线上都没有；下次 autogenerate 对比时，还会生成一些莫名其妙的改动。

**两个人同时改表会冲突**。比如都在 `8b00b78b9f87` 上，A 加了 `priority`，B 加了 `due_date`，各自生成一个迁移。两边代码合并后，就有了两个「最新版本」：

```bash
$ alembic heads                 # 列出所有最新版本：本来只该有一个
c6314163489a (head)
affb685abc68 (head)

$ alembic upgrade head          # 不知道该升到哪一个，直接报错
FAILED: Multiple head revisions are present for given argument 'head'; please specify a specific target revision, '<branchname>@head' to narrow to a specific head, or 'heads' for all heads
```

两种解决办法，选一种：

**① 接到对方后面（还没上线时用）**：后合并的人打开自己的迁移脚本，把 `down_revision` 改成对方的版本号。两个迁移就变成一前一后，又只剩一个最新版本：

```python
# migrations/versions/affb685abc68_add_task_due_date.py（B 的脚本）
down_revision: Union[str, Sequence[str], None] = 'c6314163489a'   # 原来是 '8b00b78b9f87'，改成 A 的版本号
```

```bash
$ alembic upgrade head
Running upgrade 8b00b78b9f87 -> c6314163489a, add task priority
Running upgrade c6314163489a -> affb685abc68, add task due_date
```

**② 生成一个合并脚本（已经有人执行过其中一个时用）**：脚本里什么都不做，只是把两条线接起来：

```bash
$ alembic merge heads -m "merge priority and due_date"
$ alembic upgrade head
Running upgrade 8b00b78b9f87 -> affb685abc68, add task due_date
Running upgrade 8b00b78b9f87 -> c6314163489a, add task priority
Running upgrade c6314163489a, affb685abc68 -> c2b738282283, merge priority and due_date
```

```python
# 生成的合并脚本：down_revision 是两个版本号，upgrade / downgrade 里都是 pass
down_revision: Union[str, Sequence[str], None] = ('c6314163489a', 'affb685abc68')
```

已经在线上或同事库里执行过的迁移，不能再改它的 `down_revision`（下面「已经执行过、提交过的迁移脚本不要再改」），这时只能用 ②。

### 常用命令

| 命令 | 作用 |
|---|---|
| `alembic revision --autogenerate -m "说明"` | 对比模型和数据库，生成迁移脚本 |
| `alembic upgrade head` | 升到最新 |
| `alembic downgrade -1` | 回退一个版本 |
| `alembic current` | 数据库现在在哪个版本 |
| `alembic history` | 所有版本，从新到旧 |

```
$ alembic history
8b00b78b9f87 -> c6314163489a (head), add task priority
<base> -> 8b00b78b9f87, create users and tasks
```

- **生成的脚本一定要打开看一眼再 upgrade**。autogenerate 不是万能的：比如把列**改名**，它会识别成「删掉旧列 + 加一列新的」，数据就丢了。这种要手动把脚本改成 `op.alter_column('tasks', '旧名', new_column_name='新名')`。
- **已经执行过、提交过的迁移脚本不要再改**。要改就再生成一个新的。

## 3.16 上线：CORS、中间件、部署 {#deploy}

最后三件事：让浏览器里的前端能调到接口，给每个请求记日志，部署到线上。

### CORS：跨域

前端在 `http://localhost:5173`，后端在 `http://localhost:8000`，端口不同就算**不同的源**。浏览器出于安全，默认不让网页读别的源返回的数据。这时候浏览器会先问后端一句（发一个 `OPTIONS` 请求，叫**预检**）：「`localhost:5173` 的页面能调你吗？」后端回答可以，浏览器才把真正的请求发出去。

所以 CORS 是**后端**的配置，前端改不了。FastAPI 用自带的中间件：

```python
# app/main.py（先看写法，下面「完整的 main.py」里会放到一起）
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(                      # 给 app 加一个中间件
    CORSMiddleware,                      # FastAPI 自带的跨域中间件，会自动回答 OPTIONS 预检
    allow_origins=settings.cors_origins, # 允许哪些前端网址，从配置里读
    allow_methods=["*"],                 # 所有请求方法
    allow_headers=["*"],                 # 所有请求头，包括 Authorization
)
```

`app/config.py` 加一个配置，线上把前端的正式网址写进去：

```python
    # app/config.py（Settings 类里加上）
    cors_origins: list[str] = ["http://localhost:5173"]   # 允许跨域的前端网址；环境变量写成 JSON：CORS_ORIGINS='["https://todo.example.com"]'
```

- **`allow_origins` 写具体网址，不要图省事写 `["*"]`**。本笔记站的后端写的是 `*`，因为它的 token 在请求头里、不用 Cookie，任何网页都拿不到别人的 token，开放也没风险。用 Cookie 登录的项目绝不能写 `*`（这种情况浏览器也不允许）。
- 用 curl、Postman 调接口不会遇到跨域：CORS 只是浏览器的限制。所以「Postman 能通、浏览器报 CORS」就是这个问题。

### 中间件：每个请求都经过的地方

**中间件**包在所有接口外面：请求进来先经过它，再到接口；接口的响应出去，也要再经过它。适合放「每个请求都要做」的事：记日志、统计耗时、加响应头。上面的 CORS 也是一个中间件。

```python
# app/main.py（先看写法，下面「完整的 main.py」里会放到一起）
import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")   # 日志格式：时间 级别 内容（第 2.3 节）
logger = logging.getLogger("todo-api")


@app.middleware("http")                          # 登记成中间件：每个 HTTP 请求都会经过它
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:   # call_next：调用它就是「交给后面处理」
    start = time.perf_counter()                  # 接口执行前：记下开始时间
    response = await call_next(request)          # 交给后面的路由去处理，拿到响应
    ms = (time.perf_counter() - start) * 1000    # 接口执行后：算出用了多少毫秒
    logger.info("%s %s → %s %.0fms", request.method, request.url.path, response.status_code, ms)   # 打印：GET /tasks → 200 3ms
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"   # 也可以改响应：加个响应头
    return response                              # 把响应交回去，发给前端
```

```
2026-11-12 19:59:24,565 INFO GET / → 200 7ms
2026-11-12 19:59:24,574 INFO GET /tasks → 401 1ms
```

`call_next(request)` 之前的代码在接口执行**前**跑，之后的在接口执行**后**跑，和 2.8 节 `yield` 前后是一个意思。日志用 2.3 节的 `logging`，不用 `print`：线上能按级别过滤，也能统一收集。

**顺序有没有要求**：

- **和路由谁先谁后都行**：中间件包在整个 app 外面，不是包在某个路由外面。先 `include_router` 再加中间件，照样对所有接口生效。唯一的要求是在服务启动前加好，写在 `main.py` 里就满足；启动后再加会报 `RuntimeError: Cannot add middleware after an application has started`。
- **多个中间件之间：后加的在外层，先执行**。每加一个就往外多包一层：

```
# 先加 A，再加 B
请求 → B → A → 接口 → A → B → 响应
```

下面完整的 `main.py` 里，CORS 先加、日志中间件后加，日志在最外层，浏览器的 `OPTIONS` 预检也会记进日志。反过来让 CORS 在最外层的话，预检由 CORS 直接回 200，根本走不到日志中间件，日志里就看不到预检。

完整的 `main.py`，分四块：

**开头：导入、日志**

```python
# app/main.py（整个换成这样）
from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app import errors
from app.config import settings
from app.response import success              # 健康检查要用
from app.routers import auth, tasks

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")   # 日志格式
logger = logging.getLogger("todo-api")

app = FastAPI(title="todo-api")         # 不再 create_all：表结构交给 alembic
errors.install(app)                     # 登记错误处理器
```

**跨域**

```python
# app/main.py（接着写）
app.add_middleware(                     # 跨域：允许这些网址的前端页面调接口
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # 从配置里读允许的网址
    allow_methods=["*"],                 # 所有请求方法
    allow_headers=["*"],                 # 所有请求头，包括 Authorization
)
```

**中间件：给每个请求记日志**

```python
# app/main.py（接着写）
@app.middleware("http")                          # 每个请求进来、出去都会经过这里
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start = time.perf_counter()                  # 接口执行前
    response = await call_next(request)          # 交给后面的路由去处理，拿到响应
    ms = (time.perf_counter() - start) * 1000    # 接口执行后：用了多少毫秒
    logger.info("%s %s → %s %.0fms", request.method, request.url.path, response.status_code, ms)
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"   # 也可以改响应：加个响应头
    return response
```

**挂路由、健康检查**

```python
# app/main.py（接着写）
app.include_router(auth.router)          # /auth/...
app.include_router(tasks.router)         # /tasks/...


@app.get("/", tags=["健康检查"])         # GET /，/docs 里单独一组
def health() -> dict:
    """部署后先访问这个，确认服务起来了。"""
    return success({"status": "ok"})          # {"code": 200, "msg": "ok", "data": {"status": "ok"}}
```

加一个 `/` 接口当**健康检查**：部署完先访问它，返回 `ok` 说明服务起来了；也可以交给监控定时访问。

### 部署到 Vercel

本笔记站的后端（仓库里的 `backend/` 目录）就是这么部署的，可以对照着看。

**1. 线上数据库**：Vercel 上的服务连不到你电脑上的 Postgres，线上要用云数据库。在 Vercel 项目的 Storage 里一键建一个 Neon（Postgres，有免费额度），它会自动设好 `DATABASE_URL` 环境变量。它给的地址开头是 `postgresql://`，要改成 `postgresql+psycopg://`，否则 SQLAlchemy 会去找另一个没装的驱动 psycopg2。

**2. 入口文件和依赖**：项目根目录加一个 `index.py`，Vercel 找到里面的 `app` 就能运行：

```python
# Vercel 的入口：找到这个文件里的 app 就能跑
from app.main import app  # noqa: F401
```

依赖写进 `pyproject.toml`（2.2 节）或 `requirements.txt`，Vercel 会自动安装。`uvicorn`、`pytest` 这类只在本地用的不用写进去。

**3. 连接池和密钥**：`app/config.py` 加一个 `vercel` 配置和一个检查，改动比较多，整个文件给出来：

```python
# app/config.py（整个换成这样：标 ①②③④ 的是这次改的）
from __future__ import annotations

from pydantic import model_validator          # ① 导入：做「所有字段读完之后」的检查
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET = "dev-secret-change-me"           # ② 开发用的默认密钥单独起个名字，下面要拿它比较


class Settings(BaseSettings):                 # 继承 BaseSettings：字段从环境变量读
    """所有配置都在这里：先读环境变量，没有再读 .env，都没有用默认值。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://localhost:5432/todo"
    debug: bool = False
    jwt_secret: str = DEV_SECRET              # ③ 默认值改成用上面的常量（3.13 节加的）
    token_days: int = 7
    cors_origins: list[str] = ["http://localhost:5173"]   # 上面「跨域」加的
    vercel: bool = False                      # ④ Vercel 上会自动设置 VERCEL=1

    @model_validator(mode="after")            # 所有字段读完之后再执行这个检查
    def check_secret(self) -> Settings:
        if self.vercel and self.jwt_secret == DEV_SECRET:   # 线上还在用开发密钥，等于谁都能伪造 token
            raise ValueError("线上必须设置 JWT_SECRET 环境变量")   # 直接启动失败，比悄悄上线好
        return self                           # 检查通过，原样返回


settings = Settings()   # 整个项目共用这一个，别处 from app.config import settings
```

`app/db.py` 里，在 Vercel 上不用连接池：

```python
# app/db.py（engine 那一段改成这样）
from sqlalchemy.pool import NullPool

engine = create_engine(
    settings.database_url,
    echo=settings.debug,                                 # debug 时打印每条 SQL
    poolclass=NullPool if settings.vercel else None,     # Vercel 上不用连接池，用完就关；None = 用默认的连接池
)
```

**4. 环境变量**：在 Vercel 项目的 Settings → Environment Variables 里加上：

| 变量 | 值 |
|---|---|
| `DATABASE_URL` | Neon 的地址（开头改成 `postgresql+psycopg://`） |
| `JWT_SECRET` | `python -c "import secrets; print(secrets.token_urlsafe(32))"` 生成的随机串 |
| `CORS_ORIGINS` | `["https://你的前端网址"]` |

**5. 建表**：Vercel 不会帮你执行迁移。在本地把 `DATABASE_URL` 临时指向线上库，执行一次：

```bash
DATABASE_URL='postgresql+psycopg://...线上地址...' alembic upgrade head
```

以后每次有新的迁移，都要先这样升级线上库，再部署新代码。顺序反了的话，新代码会去读还不存在的列，直接报错。

**6. 部署和检查**：推到 GitHub，Vercel 自动部署。部署完访问 `https://你的后端域名/`，返回 `{"code":200,"msg":"ok","data":{"status":"ok"}}` 就成功了，再到 `/docs` 里注册、登录、建任务走一遍。

> 国内访问 `*.vercel.app` 经常不通（域名被污染），自己测试需要开代理；给别人用的话，绑一个自己的域名。

### 阶段三做完了什么

从 3.1 的一个 hello 接口，到现在是一个能上线的多用户后端：

| 能力 | 在哪一节 |
|---|---|
| 接口、参数、请求体校验 | 3.2、3.3 |
| 统一的响应格式和错误处理 | 3.4～3.5 |
| 手写 SQL、Postgres 和 MySQL 的区别 | 3.6 |
| 数据库增删改查、依赖注入 | 3.7～3.10 |
| 自动化测试 | 3.11 |
| 按业务拆文件、配置管理 | 3.12 |
| 注册登录、密码哈希、JWT | 3.13 |
| 数据隔离、一对多、分页 | 3.14 |
| 数据库迁移、换 Postgres | 3.15 |
| 跨域、请求日志、部署 | 3.16 |

接下来的阶段四，就是在这样的后端里接入大模型。

---

# 阶段四：AI 应用开发

这个阶段在后端里接入大模型：先学会调模型、控制成本和出错，再让模型按格式输出、调用你写的函数，最后把回答一个字一个字推给前端。

**学完这个阶段，你将会：**

- 用 OpenAI SDK 调大模型，看懂消息结构、Token 和返回结果（4.1～4.2）
- 算出每次调用花了多少钱，处理超时、重试和并发限制（4.3）
- 让模型输出固定格式的 JSON，用 Pydantic 校验（4.4）
- 让模型调用你写的函数：查数据、改数据（4.5）
- 流式输出，用 SSE 把回答实时推给前端（4.6）

示例用 **DeepSeek** 的模型。它兼容 OpenAI 的接口格式，代码用的是 `openai` 这个 SDK；换成通义千问、Kimi、智谱，甚至 OpenAI 本身，一般只改 `base_url`、key 和模型名。

## 4.1 第一次调用大模型 {#llm-call}

### 准备：key 和项目

1. 在 DeepSeek 开放平台（platform.deepseek.com）注册、充值，在「API keys」里创建一个 key（`sk-` 开头，只显示一次）。
2. key 写进环境变量，**不要写进代码、不要提交到 git**：

```bash
echo 'export DEEPSEEK_API_KEY=你的key' >> ~/.zshrc   # 写进 zsh 的配置，以后每个终端都有
source ~/.zshrc                                       # 当前终端立刻生效
echo ${#DEEPSEEK_API_KEY}                             # 只看长度，确认设上了（不会打印 key 本身）
```

3. 建一个新项目，这个阶段的代码都放在这里：

```bash
mkdir ai-demo && cd ai-demo
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install openai          # OpenAI 官方 SDK，调 DeepSeek 也用它
```

### 最小的一次调用

```python
# hello_llm.py
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],   # 从环境变量读 key
    base_url="https://api.deepseek.com",      # 发到 DeepSeek，不写就是发到 OpenAI
)

resp = client.chat.completions.create(        # 发一次请求，等模型整段回答完才返回
    model="deepseek-flash",                   # 用哪个模型
    messages=[{"role": "user", "content": "用一句话介绍 FastAPI"}],   # 对话内容，下一节细讲
    extra_body={"thinking": {"type": "disabled"}},   # 关掉思考模式，见下面
)

print(resp.choices[0].message.content)        # 模型的回答
# FastAPI 是一个基于 Python 类型提示构建的现代、高性能 Web 框架，用于快速开发 API，支持自动生成交互式文档并具备异步能力。
print(resp.choices[0].finish_reason)          # stop：正常说完了
print(resp.usage.prompt_tokens, resp.usage.completion_tokens, resp.usage.total_tokens)
# 9 34 43                                     输入 9 个 token，输出 34 个，一共 43 个（按 token 收费）
```

`resp` 是一个对象，最常用的就是这几个字段：

```python
resp.choices[0].message.content    # 回答的文字
resp.choices[0].finish_reason      # 为什么停：stop 说完了 / length 到了长度上限被截断 / tool_calls 要调用函数（4.5 节）
resp.usage                         # 用了多少 token：算钱、看上下文有多长都靠它
resp.model                         # 实际用的模型
```

`choices` 是列表，是因为接口允许一次要多个候选回答；平时只要一个，固定写 `choices[0]`。

### 选模型、思考模式

DeepSeek 现在有两个模型：

| 模型 | 特点 | 用在哪 |
|---|---|---|
| `deepseek-flash` | 快、便宜 | 大部分场景：对话、提取信息、调用函数，本阶段都用它 |
| `deepseek-v4-pro` | 更强、更贵 | 复杂推理、写长代码 |

两个模型**默认开着思考模式**：先在内部推理一遍再回答，推理的内容也按输出 token 收费。简单任务关掉更快、更省钱。

为了少写重复代码，先把 client 抽到一个文件里，后面的例子都 `from llm import ...`：

```python
# llm.py
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
MODEL = "deepseek-flash"
NO_THINKING = {"thinking": {"type": "disabled"}}   # 关掉思考模式
```

```python
# think.py：不关思考模式，看看多了什么
from llm import client

resp = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "user", "content": "一个笼子里有鸡和兔，共 10 个头、28 只脚，鸡兔各几只？只给答案"}],
)
msg = resp.choices[0].message
print(msg.content)                     # 鸡6只，兔4只。
print(msg.reasoning_content[:100])     # 思考过程，和 content 平级：
# We need answer only. Need compute. Let chicken x rabbit y. x+y=10, 2x+4y=28 => x+2y=14 => subtract x
print(resp.usage.completion_tokens, resp.usage.completion_tokens_details.reasoning_tokens)
# 76 67                                输出 76 个 token，其中 67 个是思考：答案本身只有 9 个
```

- **关思考**：`extra_body={"thinking": {"type": "disabled"}}`。`extra_body` 是 openai SDK 留的口子：OpenAI 自己没有、DeepSeek 特有的参数放这里。
- 本阶段的例子都关掉思考；数学、逻辑、写代码这类难题再打开。

> 模型名、价格会变，以 DeepSeek 的 API 文档（api-docs.deepseek.com）为准。写错模型名会直接 400，报错里会列出现在支持的名字。

## 4.2 消息结构、System Prompt、Token {#messages-tokens}

### 消息有三种角色

`messages` 是一个列表，每条消息是 `{"role": 角色, "content": 内容}`：

| role | 是谁 | 用来 |
|---|---|---|
| `system` | 开发者 | 定规则：你是谁、怎么回答、不能做什么。放第一条 |
| `user` | 用户 | 用户说的话 |
| `assistant` | 模型 | 模型之前的回答（多轮对话时自己带上） |

后面 4.5 节还会用到第四种 `tool`：函数的执行结果。

### System Prompt：定规则

```python
# sys_demo.py
from llm import MODEL, NO_THINKING, client

question = {"role": "user", "content": "Python 和 JavaScript 有什么区别？"}

# ① 不加 system：模型按自己的习惯回答
resp = client.chat.completions.create(model=MODEL, messages=[question], extra_body=NO_THINKING)
print(resp.choices[0].message.content[:60])   # 只看开头：写了一篇带标题、带表格的长文
# # Python 和 JavaScript 的区别
#
# Python 和 JavaScript 是两门非常流行但设计理念差
print(resp.usage.completion_tokens)           # 765

# ② 加 system：按你定的规则回答
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是编程老师。回答不超过 30 个字，不用 Markdown。"},
        question,
    ],
    extra_body=NO_THINKING,
)
print(resp.choices[0].message.content)        # Python 重可读和数据分析，JS 重浏览器和网页交互。
print(resp.usage.completion_tokens)           # 16：输出少了，钱也少了
```

AI 应用里大部分「功能」，其实就是写好的 system prompt：客服、翻译、提取信息，换的主要是这一段。它由后端写死，用户看不到也改不了。

### 模型没有记忆：多轮对话要自己带上历史

每次调用都是独立的，模型不记得上一次说了什么。想让它「记得」，就把之前的对话全部放进 `messages` 再发一次：

```python
# history_demo.py
from llm import MODEL, NO_THINKING, client


def ask(messages):
    resp = client.chat.completions.create(model=MODEL, messages=messages, extra_body=NO_THINKING)
    return resp.choices[0].message.content, resp.usage.prompt_tokens   # 回答、这次输入了多少 token


print(ask([{"role": "user", "content": "我叫什么？"}]))
# ('你好！😊 从我们的对话中，我并不知道你的名字——你还没有告诉我呢。...', 7)

history = [{"role": "system", "content": "回答不超过 20 个字。"}]
for text in ["我叫小林，在学 Python", "我叫什么？", "我在学什么？"]:
    history.append({"role": "user", "content": text})          # ① 用户的话加进历史
    answer, prompt_tokens = ask(history)                       # ② 整个历史发过去
    history.append({"role": "assistant", "content": answer})   # ③ 模型的回答也加进历史，下一轮带上
    print(text, "→", answer, prompt_tokens)
# 我叫小林，在学 Python → 你好小林！Python 学习加油，有什么问题可以问我。 18
# 我叫什么？ → 你叫小林。 38
# 我在学什么？ → 你在学 Python。 50
print(len(history))                                            # 7：1 条 system + 3 轮 × 2 条
```

最后一列是每轮的输入 token：**18 → 38 → 50，越聊越多**，因为每次都把全部历史重新发一遍，每次都按全部历史收费。聊天产品里的「新建对话」，就是清空这个列表。

### Token：按它收费，也按它限制长度

模型不是按字、按单词处理文字，而是切成 **token**。DeepSeek 文档给的估算：1 个中文字约 0.6 个 token，1 个英文字母约 0.3 个 token。实测一下：

```python
# token_demo.py
from llm import MODEL, NO_THINKING, client


def count_tokens(text):
    resp = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": text}], max_tokens=1, extra_body=NO_THINKING,
    )                                          # max_tokens=1：只想看输入有多少 token，回答只要 1 个
    return resp.usage.prompt_tokens


zh = "今天天气不错，我们去公园散步吧。" * 10
en = "The weather is nice today, let's go for a walk in the park. " * 10
print(len(zh), count_tokens(zh))   # 160 94    160 个字 → 94 个 token，约 0.6
print(len(en), count_tokens(en))   # 600 165   600 个字母 → 165 个 token，约 0.3
```

- **准确的数字以 `resp.usage` 为准**，估算只用来心里有数。
- **上下文长度**：一次请求里输入加输出最多能有多少 token。DeepSeek 现在是 1M（一百万）。超过就报错，长对话要裁剪历史（阶段五细讲）。
- **`max_tokens`**：限制这次最多输出多少个 token。到了上限就硬截断，`finish_reason` 变成 `length`：

```python
# token_demo.py（接着写）
resp = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": "详细介绍一下 FastAPI"}], max_tokens=30, extra_body=NO_THINKING,
)
print(resp.choices[0].message.content)
# # FastAPI 详细介绍
#
# ## 一、什么是 FastAPI
#
# FastAPI 是一个现代、快速（高性能）的 Python Web 框架，
print(resp.choices[0].finish_reason, resp.usage.completion_tokens)   # length 30   话没说完就被截断了
```

拿到回答要先看 `finish_reason`：是 `length` 就说明内容不完整，不能直接当结果用（4.4 节解析 JSON 时尤其要注意）。

## 4.3 成本、超时、重试、限流 {#cost-retry}

### 算钱：按 token 和缓存

DeepSeek 按每百万 token 收费，输入分两种价格：

| deepseek-flash（美元 / 百万 token） | 高峰 | 非高峰（半价） |
|---|---|---|
| 输入，命中缓存 | 0.006 | 0.003 |
| 输入，没命中缓存 | 0.3 | 0.15 |
| 输出 | 1.2 | 0.6 |

- **高峰时段**：工作日北京时间 9:00～12:00、14:00～18:00，其他时间（含周末、法定节假日）半价。
- **缓存**：如果这次请求的开头和之前的请求一样（比如同一段很长的 system prompt），重复的那部分按「命中缓存」算，便宜得多，DeepSeek 自动做，不用配置。
- 价格会调整，以文档的价格页为准。

`usage` 里有命中、没命中各多少 token，按单价乘一下就是这次花的钱：

```python
# cost_demo.py
from llm import MODEL, NO_THINKING, client

PRICE = {"hit": 0.006, "miss": 0.3, "output": 1.2}   # deepseek-flash 高峰价，美元 / 百万 token


def cost_usd(usage):
    hit = usage.prompt_cache_hit_tokens       # 输入里命中缓存的 token
    miss = usage.prompt_cache_miss_tokens     # 输入里没命中的 token
    out = usage.completion_tokens             # 输出的 token
    return (hit * PRICE["hit"] + miss * PRICE["miss"] + out * PRICE["output"]) / 1_000_000


rules = "你是 todo 应用的客服。规则：" + "回答要礼貌、简短，只回答和 todo 应用有关的问题。" * 50   # 故意弄一段很长的 system
for q in ["怎么新建任务？", "怎么删除任务？"]:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": rules}, {"role": "user", "content": q}],
        extra_body=NO_THINKING,
    )
    u = resp.usage
    print(u.prompt_cache_hit_tokens, u.prompt_cache_miss_tokens, u.completion_tokens, f"{cost_usd(u):.6f}")
# 0 767 25 0.000260      第一次：767 个输入 token 全没命中
# 512 255 22 0.000106    第二次：开头一样的 512 个命中缓存，钱少了一半多
```

- **省钱规则**：固定不变的内容（system prompt、文档资料）放在 `messages` 最前面，每次变的内容（用户问题）放后面，这样开头才能命中缓存。
- 正式项目里，每次调用都把 `usage` 和算出来的钱记进日志或数据库，按用户、按功能统计，才知道钱花在哪。

### 超时和重试：SDK 自带

调模型比一般接口慢得多，几秒到几十秒都正常，网络抖动、服务繁忙也常见。openai SDK 自带超时和重试，**创建 client 时设好就行**：

```python
# error_demo.py
import os
import time

import openai
from openai import OpenAI

from llm import MODEL, NO_THINKING

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
    timeout=30,        # 一次请求最多等 30 秒（默认等 600 秒，太长了）
    max_retries=2,     # 超时、连不上、429、5xx 时自动重试 2 次（默认就是 2）
)
print(client.timeout, client.max_retries)   # 30 2

msgs = [{"role": "user", "content": "写一篇 500 字的文章"}]
start = time.perf_counter()
try:
    client.chat.completions.create(model=MODEL, messages=msgs, extra_body=NO_THINKING, timeout=1)   # 单次请求也能覆盖：故意只等 1 秒
except openai.APITimeoutError as e:
    print(type(e).__name__, e, round(time.perf_counter() - start, 1))
# APITimeoutError Request timed out. 4.8    一共试了 3 次（1 次 + 重试 2 次），每次 1 秒，中间还等了一会儿
```

SDK 的重试就是 2.6 节手写的那一套：只重试「可能下次就好」的错误，越等越久，次数有上限。

### 常见错误

openai SDK 把 HTTP 错误转成了不同的异常类，按类型 `except`：

| 状态码 | 异常类 | DeepSeek 的意思 | 怎么办 | SDK 会自动重试吗 |
|---|---|---|---|---|
| 400 | `BadRequestError` | 请求格式不对：模型名写错、参数不对 | 看报错改代码 | 不会 |
| 401 | `AuthenticationError` | key 不对 | 检查 key | 不会 |
| 402 | `APIStatusError` | 余额不足 | 充值 | 不会 |
| 422 | `UnprocessableEntityError` | 参数值不对 | 看报错改代码 | 不会 |
| 429 | `RateLimitError` | 并发太多 | 降低并发，见下面 | 会 |
| 500 / 503 | `InternalServerError` | 服务器出错 / 太忙 | 等一会儿再试 | 会 |
| — | `APITimeoutError` | 等太久没回 | 调大超时或换短一点的任务 | 会 |

```python
# error_demo.py（接着写）
bad = OpenAI(api_key="sk-wrong", base_url="https://api.deepseek.com")   # 故意用错的 key
try:
    bad.chat.completions.create(model=MODEL, messages=msgs)
except openai.AuthenticationError as e:
    print(e.status_code, e.message)
# 401 Error code: 401 - Authentication Fails, Your api key: ****rong is invalid (request_id: ...)

try:
    client.chat.completions.create(model="deepseek-xxx", messages=msgs)   # 故意写错模型名
except openai.BadRequestError as e:
    print(e.status_code, e.message)
# 400 Error code: 400 - The supported API model names are deepseek-flash, deepseek-v4-pro, but you passed deepseek-xxx. (request_id: ...)
```

在 FastAPI 接口里调模型时，这些异常要接住，转成 3.5 节的统一错误格式返回给前端，不要把原始报错直接抛出去。

### 限流：控制同时发出去的请求数

DeepSeek 不限每分钟请求数，限的是**同时进行中的请求数**（并发）：一个请求从发出到模型回答完都算占着一个名额，超过就返回 429。

要批量调用时（比如一次翻译 100 条），用 2.5 节的 `asyncio.Semaphore` 控制并发。异步要用 `AsyncOpenAI`，用法和 `OpenAI` 一样，调用前加 `await`：

```python
# limit_demo.py
import asyncio
import os
import time

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
limit = asyncio.Semaphore(3)                   # 最多同时 3 个请求


async def translate(word):
    async with limit:                          # 拿到名额才往下走，满了就排队等
        start = time.perf_counter()
        resp = await client.chat.completions.create(   # 异步调用，等的时候别的任务可以跑
            model="deepseek-flash",
            messages=[{"role": "user", "content": f"把「{word}」翻译成英文，只回答单词"}],
            extra_body={"thinking": {"type": "disabled"}},
        )
        print(word, resp.choices[0].message.content, f"{time.perf_counter() - start:.1f}s")
        return resp.choices[0].message.content


async def main():
    start = time.perf_counter()
    words = ["苹果", "香蕉", "西瓜", "葡萄", "橙子", "草莓"]
    results = await asyncio.gather(*(translate(w) for w in words))   # 6 个一起提交，同时只跑 3 个
    print(results, f"共 {time.perf_counter() - start:.1f}s")


asyncio.run(main())
# 苹果 Apple 0.5s
# 香蕉 banana 0.5s
# 西瓜 Watermelon 0.5s
# 橙子 Orange 0.4s
# 葡萄 grape 0.4s
# 草莓 strawberry 1.0s
# ['Apple', 'banana', 'Watermelon', 'grape', 'Orange', 'strawberry'] 共 1.5s
```

- 6 个请求一个一个调要 3 秒左右，3 个并发 1.5 秒就完了。
- `gather` 返回的结果顺序和传进去的顺序一致，不管谁先完成。
- 在 FastAPI 接口里调模型也要用 `AsyncOpenAI`（接口写成 `async def`），否则一个请求等模型的几秒钟里会卡住其他请求。

## 4.4 Structured Output：让模型输出 JSON {#structured-output}

模型默认输出的是一段话，程序很难用。要拿去存数据库、给前端渲染，就得让它输出**固定格式的 JSON**，再用 3.3 节的 Pydantic 校验。

例子：用户随口说一句话，提取成一个待办任务。

```python
# json_demo.py
from typing import Literal

import openai
from pydantic import BaseModel, Field, ValidationError

from llm import MODEL, NO_THINKING, client


class TaskDraft(BaseModel):                       # 想要的格式，和 3.3 节写请求体一样
    title: str = Field(max_length=50)
    priority: Literal["high", "medium", "low"]    # 只能是这三个之一
    due: str | None                               # 截止日期，没有就是 None


# system 里写清楚：① 必须出现 json 这个词 ② 给一个格式示例
SYSTEM = """从用户的话里提取一个待办任务，只输出 json，格式：
{"title": "任务标题", "priority": "high / medium / low 三选一", "due": "截止日期 YYYY-MM-DD，没说就是 null"}"""


def extract(text: str) -> TaskDraft:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        response_format={"type": "json_object"},  # JSON 模式：保证输出是合法的 JSON
        max_tokens=200,                           # 留够长度，被截断的 JSON 解析不了
        extra_body=NO_THINKING,
    )
    content = resp.choices[0].message.content
    print(content)                                # 模型输出的 JSON 字符串
    return TaskDraft.model_validate_json(content) # 解析 + 校验，不合格就抛 ValidationError


task = extract("下周五之前一定要把季度报告交了，今天是 2026-11-20")
# {"title": "提交季度报告", "priority": "high", "due": "2026-11-27"}
print(task)            # title='提交季度报告' priority='high' due='2026-11-27'
print(task.priority)   # high                     已经是 TaskDraft 对象，直接用点号取
```

「下周五」被换算成了具体日期，「一定要」被理解成了 `high`：这种「把人话变成结构化数据」，是大模型在业务里最常见的用法。

**JSON 模式的规则（记住就行）**：

1. 写 `response_format={"type": "json_object"}`。
2. prompt 里**必须出现 `json` 这个词**，否则直接 400：

```python
# json_demo.py（接着写）
try:
    client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": "提取任务：明天交报告"}],   # prompt 里没有 json
        response_format={"type": "json_object"}, extra_body=NO_THINKING,
    )
except openai.BadRequestError as e:
    print(e.message)
# Error code: 400 - Prompt must contain the word 'json' in some form to use 'response_format' of type 'json_object'. (request_id: ...)
```

3. 在 prompt 里**给出格式示例**：字段名、类型、可选值都写清楚。JSON 模式只保证「是合法 JSON」，不保证字段对。
4. **一定要用 Pydantic 校验**：模型可能少字段、多字段、值不在范围里：

```python
# json_demo.py（接着写）
try:
    TaskDraft.model_validate_json('{"title": "交报告", "priority": "urgent", "due": null}')   # 假设模型输出了 urgent
except ValidationError as e:
    print(e.errors()[0]["msg"])   # Input should be 'high', 'medium' or 'low'
```

5. 校验失败、内容为空、`finish_reason` 是 `length` 时：重试一次，还不行就给用户一个友好的报错。别把没通过校验的数据存进数据库。

> OpenAI 自己的接口支持更严格的 `json_schema` 模式：直接传 Pydantic 模型，保证字段完全对。DeepSeek 目前只支持上面的 `json_object`，所以要自己校验。不管用哪家，模型的输出都当成「前端传来的数据」一样对待：先校验再用。

## 4.5 Function Calling：让模型调用你的函数 {#function-calling}

模型只会生成文字，不能查你的数据库，也不知道今天的任务。**Function Calling**（也叫 Tool Calling）就是：你告诉模型有哪些函数可以用，模型判断需要时，返回「我要调用哪个函数、参数是什么」，**由你的代码去执行**，再把结果交回给模型，模型根据结果回答。

```
用户：我还有哪些任务没做完？
  → 模型：要调用 list_tasks(done=false)        ← 模型只是「说要调用」，不会自己执行
  → 你的代码：执行 list_tasks，得到结果
  → 把结果发回给模型
  → 模型：你还有「交季度报告」「跑步 5 公里」两个任务
```

### ① 准备函数，写给模型看的说明

```python
# tool_demo.py
import json

from llm import MODEL, NO_THINKING, client

TASKS = [                                         # 假装是数据库里的任务
    {"id": 1, "title": "写笔记", "done": True},
    {"id": 2, "title": "交季度报告", "done": False},
    {"id": 3, "title": "跑步 5 公里", "done": False},
]


def list_tasks(done: bool | None = None) -> list[dict]:   # 普通的 Python 函数
    if done is None:
        return TASKS
    return [t for t in TASKS if t["done"] == done]


def finish_task(task_id: int) -> dict:
    for t in TASKS:
        if t["id"] == task_id:
            t["done"] = True
            return {"ok": True, "task": t}
    return {"ok": False, "error": f"没有 id 为 {task_id} 的任务"}   # 出错也返回给模型，让它告诉用户


TOOLS = [                                         # 给模型看的函数说明：名字、做什么、参数（JSON Schema 格式）
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "查询用户的待办任务列表",   # 模型靠 description 判断什么时候该用，要写清楚
            "parameters": {
                "type": "object",
                "properties": {
                    "done": {"type": "boolean", "description": "true 只查已完成，false 只查未完成，不传查全部"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "把一个任务标记为已完成",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "integer", "description": "任务 id"}},
                "required": ["task_id"],          # 必须传的参数
            },
        },
    },
]

FUNCTIONS = {"list_tasks": list_tasks, "finish_task": finish_task}   # 函数名 → 真正的函数，执行时按名字找
```

### ② 模型返回的「要调用」长什么样

调用时多传一个 `tools=TOOLS`。模型决定要用函数时，回答里不是文字，而是 `tool_calls`：

```python
# tool_demo.py（接着写）
resp = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": "我还有哪些任务没做完？"}], tools=TOOLS, extra_body=NO_THINKING,
)
m = resp.choices[0].message
print(repr(m.content))           # '我来查一下你未完成的任务。'   可能带一句话，也可能是空的
for c in m.tool_calls:
    print(c.id, c.type, c.function.name, repr(c.function.arguments))
# call_00_yedAQk8XZOs2YqNUiXZn4849 function list_tasks '{"done": false}'
#   id：这次调用的编号，回传结果时要带上
#   arguments：参数是 JSON 字符串，要自己 json.loads
```

用户的话和函数无关时，模型就正常回答，`tool_calls` 是 `None`：

```python
# tool_demo.py（接着写）
resp = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": "你好"}], tools=TOOLS, extra_body=NO_THINKING,
)
print(resp.choices[0].finish_reason, resp.choices[0].message.tool_calls)   # stop None
```

### ③ 循环：调模型 → 执行函数 → 把结果交回去 → 直到模型给出最终回答

一句话可能要调好几次函数（先查、再改），所以写成循环：

```python
# tool_demo.py（接着写）
messages = [{"role": "user", "content": "我还有哪些任务没做完？把跑步那个标成完成"}]

for step in range(1, 6):                          # 最多 5 轮，防止模型一直调用停不下来
    resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING)
    msg = resp.choices[0].message
    print(f"第 {step} 次调用，finish_reason={resp.choices[0].finish_reason}")
    if not msg.tool_calls:                        # ① 不要调函数了：这就是最终回答
        print("最终回答：", msg.content)
        break
    messages.append(msg)                          # ② 模型「要调用」的这条消息，原样放进历史
    for call in msg.tool_calls:                   # ③ 一次可能要调好几个，逐个执行
        args = json.loads(call.function.arguments)                # 参数：JSON 字符串 → 字典
        print("  模型要调用：", call.function.name, args)
        result = FUNCTIONS[call.function.name](**args)            # 按名字找到函数，执行
        print("  执行结果：", result)
        messages.append({                                         # ④ 结果用 tool 角色放进历史
            "role": "tool",
            "tool_call_id": call.id,                              # 对应哪一次调用
            "content": json.dumps(result, ensure_ascii=False),    # 结果转成字符串
        })
    # 回到循环开头：带着函数结果再调一次模型
```

实际运行：

```
第 1 次调用，finish_reason=tool_calls
  模型要调用： list_tasks {'done': False}
  执行结果： [{'id': 2, 'title': '交季度报告', 'done': False}, {'id': 3, 'title': '跑步 5 公里', 'done': False}]
第 2 次调用，finish_reason=tool_calls
  模型要调用： finish_task {'task_id': 3}
  执行结果： {'ok': True, 'task': {'id': 3, 'title': '跑步 5 公里', 'done': True}}
第 3 次调用，finish_reason=stop
最终回答： 搞定了。你原本有两个未完成的任务：

1. **交季度报告** —— 还没做完
2. **跑步 5 公里** —— ✅ 已标记完成

现在就剩「交季度报告」这一项了，加油 💪
```

用户只说了「跑步那个」，模型自己先查出列表，再找到跑步是 id 3，然后调用 `finish_task(3)`。

**规则（记住就行）**：

- **函数由你的代码执行**，模型只给出名字和参数。参数也可能不对，要和接口参数一样校验（可以用 Pydantic）。
- **一定要限制最大轮数**，模型可能反复调用停不下来。
- **函数执行出错也要把错误交回给模型**（像 `finish_task` 找不到 id 那样），让它告诉用户，而不是让程序崩掉。
- **删除、付款这类高风险操作**，不要让模型直接执行，先返回给用户确认（阶段五细讲）。
- 在接口里用时，函数要按当前登录用户查数据（3.14 节的 `user_id`），不能因为是模型调用就跳过权限检查。

这个「调模型 → 执行工具 → 结果交回 → 再调模型」的循环，就是 Agent 最核心的部分，阶段五会在这个基础上展开。

## 4.6 流式输出和 SSE {#streaming-sse}

模型写一段几百字的回答要好几秒。前面的调用都是等全部写完才返回，用户要盯着空白页等。**流式输出**：模型生成一点就返回一点，前端一个字一个字地显示，用户马上就能看到内容。

### Python 里接收流式输出

加 `stream=True`，返回的不再是一个完整结果，而是可以 `for` 的一串片段（chunk）：

```python
# stream_demo.py
from llm import MODEL, NO_THINKING, client

stream = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "用三句话介绍 Python"}],
    stream=True,                               # 流式：边生成边返回
    stream_options={"include_usage": True},    # 最后多给一个片段，带上 usage（流式默认不给）
    extra_body=NO_THINKING,
)

parts = []                                     # 把片段攒起来，最后拼成完整回答
for i, chunk in enumerate(stream):             # 每生成一点，循环就走一次
    if i < 3:                                  # 看看前 3 个片段装的是什么
        print(repr(chunk.choices[0].delta.content) if chunk.choices else None)
    if chunk.choices and chunk.choices[0].delta.content:   # 片段里的文字在 delta.content，不是 message.content
        parts.append(chunk.choices[0].delta.content)
    if chunk.usage:                            # 最后那个片段：choices 是空的，只有 usage
        print("usage:", chunk.usage.prompt_tokens, chunk.usage.completion_tokens, "chunks:", i + 1)
print("".join(parts))
```

```
''
'1'
'.'
usage: 9 69 chunks: 71
1. Python 是一种语法简洁、易读易学的高级编程语言，广泛适用于数据分析、人工智能、Web 开发等众多领域。  
2. 它拥有丰富的标准库和第三方生态，能大幅提升开发效率。  
3. Python 跨平台、社区活跃，是编程入门与快速原型的理想选择。
```

- 每个片段只有一两个字，69 个 token 的回答分成了 71 个片段返回。
- 第一个片段的文字常常是空字符串，要判断一下再用。
- 想在终端里看到打字效果，把 `parts.append` 换成 `print(text, end="", flush=True)`。

### SSE：后端把片段推给前端

后端拿到片段后，要一个个转发给浏览器。最常用的格式是 **SSE**（Server-Sent Events）：一个普通的 HTTP 响应，`Content-Type` 是 `text/event-stream`，连接不断开，后端往里一段段写：

```
event: delta              ← 事件名，自己定
data: {"text": "你好"}     ← 数据，一般写 JSON

event: done               ← 每个事件之间空一行
data: {"length": 54}

```

规则就这三条：每行 `字段: 值`；一个事件以**空行**结束；`data` 里放 JSON 字符串。

FastAPI 用 `StreamingResponse` 加一个生成器（2.8 节 `yield`）实现，再装两个包：`uv pip install fastapi uvicorn`。

```python
# chat_api.py
import json
import os
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI()
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")   # 接口里用异步的


class ChatIn(BaseModel):
    question: str


def sse(event: str, data: dict) -> str:
    """拼一个 SSE 事件：event 一行、data 一行、最后一个空行。"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
async def chat_stream(body: ChatIn, request: Request) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:   # 生成器：每 yield 一次，就往响应里写一段
        stream = await client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": body.question}],
            stream=True,
            extra_body={"thinking": {"type": "disabled"}},
        )
        parts: list[str] = []
        finished = False
        try:
            async for chunk in stream:          # 异步版的 for：模型每给一个片段走一次
                if await request.is_disconnected():   # ① 前端断开了（关页面、点了停止）：不用再往下读
                    break
                text = chunk.choices[0].delta.content if chunk.choices else None
                if text:
                    parts.append(text)
                    yield sse("delta", {"text": text})   # ② 片段推给前端
            else:                               # for 正常走完（没有 break）才会进 else
                finished = True
                yield sse("done", {"length": len("".join(parts))})   # ③ 告诉前端：说完了
        except Exception as e:
            yield sse("error", {"msg": str(e)})  # ④ 中途出错：响应头已经发出去了，只能用事件告诉前端
        finally:
            await stream.close()                # ⑤ 不管怎样都关掉和模型的连接，不再继续生成、继续收费
            # ⑥ 在这里保存结果：真实项目里写进数据库，完整的还是中途断开的都要记下来
            print(f"保存回答：{'完整' if finished else '中途断开'}，{len(''.join(parts))} 个字", flush=True)

    return StreamingResponse(events(), media_type="text/event-stream")   # 把生成器包成 SSE 响应
```

启动 `uvicorn chat_api:app --port 8410`，用 curl 看原始响应（`-N`：收到一点就显示一点，不缓存）：

```bash
curl -N -X POST localhost:8410/chat/stream -H 'Content-Type: application/json' -d '{"question":"用一句话介绍 SSE"}'
```

```
event: delta
data: {"text": "SS"}

event: delta
data: {"text": "E"}

event: delta
data: {"text": "（"}

...（中间省略）

event: delta
data: {"text": "。"}

event: done
data: {"length": 54}

```

- **为什么出错要用事件告诉前端**：流式响应一开始，状态码 200 就已经发出去了，后面出错没法再改成 500，只能发一个 `error` 事件。
- **为什么要 `finally` 里保存**：用户中途关掉页面，前面生成的内容和花的钱也要记下来；不放在 `finally` 里，断开时这段代码根本不会执行。

### 前端接收：fetch + ReadableStream

浏览器自带的 `EventSource` 只能发 GET、不能带 `Authorization` 请求头，实际项目里一般用 `fetch` 自己读：

```js
// chat.mjs（前端写法；这里用 Node 运行：node chat.mjs）
async function chatStream(question, onText, signal) {
  const res = await fetch("http://localhost:8410/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },   // 要登录的接口再加 Authorization
    body: JSON.stringify({ question }),
    signal,                                            // 传 AbortController 的 signal，用来取消
  });
  const reader = res.body.getReader();                 // 响应体按块读，不等全部到齐
  const decoder = new TextDecoder();                   // 字节 → 文字
  let buffer = "";                                     // 一块里可能有半个事件，先攒着
  while (true) {
    const { done, value } = await reader.read();       // 读到一块
    if (done) break;                                   // 后端写完了
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");               // 按空行切成一个个事件
    buffer = events.pop();                             // 最后一段可能不完整，留到下一块
    for (const block of events) {
      const event = block.match(/^event: (.*)$/m)?.[1];
      const data = JSON.parse(block.match(/^data: (.*)$/m)?.[1] ?? "{}");
      if (event === "delta") onText(data.text);        // 拿到片段，追加到页面上
      if (event === "done") console.log("\n[完成] 共", data.length, "个字");
      if (event === "error") console.log("\n[出错]", data.msg);
    }
  }
}

// 正常使用：每来一个片段就追加显示
await chatStream("用两句话介绍 SSE", (t) => process.stdout.write(t));   // 浏览器里换成追加到页面元素

// 用户点「停止」：调 controller.abort()
const controller = new AbortController();
setTimeout(() => controller.abort(), 2000);            // 演示：2 秒后取消
try {
  await chatStream("写一篇 800 字的文章介绍 Python", (t) => process.stdout.write(t), controller.signal);
} catch (e) {
  console.log("\n[已取消]", e.name);                  // 取消会抛 AbortError
}
```

用 Node 实际跑了一遍（Node 18 以上也有 `fetch`）：

```
SSE（Server-Sent Events）是一种基于 HTTP 的服务器推送技术，允许服务器通过单向连接持续向客户端发送文本数据流。它适合实时通知、消息推送等场景，客户端使用 EventSource API 即可接收，并支持自动重连。
[完成] 共 119 个字

## Python：简洁优雅的编程语言

在当今数字化时代，编程语言种类繁多，而 Python 以其独特的魅力脱颖而出，成为全球最受欢迎的
[已取消] AbortError
```

后端的输出：

```
保存回答：完整，119 个字
保存回答：中途断开，69 个字
```

前端取消后，后端检测到断开，停止读取并关掉了和模型的连接，前面生成的 69 个字也保存下来了。

**规则（记住就行）**：

1. 后端用 `StreamingResponse` + 生成器，`media_type="text/event-stream"`。
2. 事件格式：`event: 名字\ndata: JSON\n\n`，用 `delta` / `done` / `error` 区分。
3. 前端用 `fetch` + `getReader()` 读，按空行切事件，半个事件留到下一块。
4. 取消：前端 `AbortController.abort()`；后端 `request.is_disconnected()` 判断，`finally` 里关掉模型连接、保存结果。
5. 部署时，Nginx 这类代理默认会把响应攒起来再发，流式就失效了，要关掉缓冲（阶段六讲）。
