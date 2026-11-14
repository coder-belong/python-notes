# AI 应用开发笔记

从 Python 基础学起，到用 FastAPI 写后端接口，再到 AI 应用和 Agent 开发。

- **阶段一：Python 语言基础**：只讲常用的写法，不常用的先跳过。
- **阶段二：Python 进阶与工程化**：类型注解、依赖管理、调试、异步、发 HTTP 请求、并发、上下文管理器。
- **阶段三：FastAPI 后端开发**：用 FastAPI + SQLAlchemy 从零做一个 todo 接口项目。

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
print("  hi  ".strip())            # 'hi' 去首尾空格
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

```python
nums = [1, 2, 3, 4]

squares = [n * n for n in nums]                 # [1, 4, 9, 16]
evens = [n for n in nums if n % 2 == 0]         # [2, 4]   带过滤条件

rows = [{"id": 1, "name": "Tom"}, {"id": 2, "name": "Jerry"}]
names = [r["name"] for r in rows]               # ['Tom', 'Jerry']
by_id = {r["id"]: r["name"] for r in rows}      # {1: 'Tom', 2: 'Jerry'}  字典推导式
print(squares, evens, names, by_id)
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

第 3.8 节的数据库会话、第 3.10 节的 pytest fixture 都用 `yield` 写「先准备 → 交出去用 → 用完收尾」，原理就是这里的「暂停再继续」。

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
- 最常见的继承是框架要求的：`class BalanceError(Exception)`（第 1.11 节）、`class TaskCreate(BaseModel)`（pydantic，第 3.3 节）、`class Task(Base)`（SQLAlchemy，第 3.6 节）。

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

写真实项目离不开的工程能力：类型注解、依赖管理、日志和配置、调试、异步、调别人的接口、并发模型。

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

`ruff check` 会指出 `os` 导入了没用（F401），`--fix` 会直接删掉那行。「准备环境」一节已经在编辑器里配了「保存时自动格式化」，平时不用手动跑；提交代码前跑一次 `ruff check` 就行。

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
db_url = os.environ.get("DATABASE_URL", "sqlite:///todo.db")   # 读环境变量 DATABASE_URL，没配就用默认值
print(db_url)                               # 没配时：sqlite:///todo.db

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

`async def` 定义的是**异步函数**：遇到要等待的操作（网络请求、sleep）时，可以先让出去执行别的任务，等好了再回来。调大模型、同时请求好几个接口都会用到。

> **先看这里**：第一遍只要看懂下面这个例子和后面的 7 条规则，就够用到阶段四。后面标了「进阶」的小节，用到再看。

```python
import asyncio
import time


async def fetch(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)       # 等待时让出去，别的任务可以先跑
    return f"{name} 好了"


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(    # 同时跑三个，等它们都完成
        fetch("A", 1), fetch("B", 1), fetch("C", 1),
    )
    print(results)                                   # ['A 好了', 'B 好了', 'C 好了']
    print(f"用时 {time.perf_counter() - start:.1f}s")  # 用时 1.0s，不是 3 秒


asyncio.run(main())                    # 程序入口启动事件循环
```

**规则，照着写就行**：

1. 异步函数用 `async def` 定义。
2. 调用异步函数要拿结果，前面必须加 `await`：`result = await fetch("A", 1)`。
3. `await` 只能写在 `async def` 里面。
4. 程序最外层用 `asyncio.run(main())` 启动，整个程序只写这一次。
5. 几件事想同时等，用 `await asyncio.gather(a(), b(), c())`，结果按顺序放在列表里。
6. 异步函数里要等一会儿，用 `await asyncio.sleep(秒)`，不能用 `time.sleep()`。
7. 写 FastAPI 时不用写 `asyncio.run`，框架会替你启动；接口用普通 `def` 也可以。

---

**下面是进阶内容**：后台任务、超时、取消、限制并发、出错处理。第一遍可以跳过，做 AI 应用调大模型时再回来看。

### create_task：先放到后台跑（进阶）

`await` 一个异步函数会一直等它做完。想让它在后台先跑着、自己接着干别的，用 `asyncio.create_task`，需要结果时再 `await`：

```python
import asyncio


async def download(name: str) -> str:
    await asyncio.sleep(1)
    return f"{name} 下载完了"


async def main() -> None:
    task = asyncio.create_task(download("a.zip"))   # 马上开始跑，不等
    print("先干点别的")
    result = await task                              # 现在才等它的结果
    print(result)


asyncio.run(main())
# 先干点别的
# a.zip 下载完了
```

`gather` 其实就是帮你把多个异步函数都 `create_task`，再一起等。

### 超时：`asyncio.timeout`（进阶）

调接口、调大模型都可能卡住，一定要设超时：

```python
import asyncio


async def slow() -> str:
    await asyncio.sleep(3)
    return "好了"


async def main() -> None:
    try:
        async with asyncio.timeout(1):     # 里面的代码超过 1 秒就取消
            print(await slow())
    except TimeoutError:
        print("超过 1 秒，不等了")


asyncio.run(main())    # 超过 1 秒，不等了
```

`asyncio.timeout` 是 Python 3.11 加的；老代码里常见的 `await asyncio.wait_for(slow(), timeout=1)` 是同一个意思。

### 取消任务（进阶）

用户关掉页面、点了「停止生成」，后台还在跑的任务要能停下来。`task.cancel()` 会在任务当前 `await` 的地方抛出 `CancelledError`：

```python
import asyncio


async def worker() -> None:
    try:
        while True:
            print("干活中")
            await asyncio.sleep(0.4)
    except asyncio.CancelledError:
        print("被取消了，收尾")       # 关连接、存进度之类的清理放这里
        raise                        # 清理完要接着抛出去，不能把取消吞掉


async def main() -> None:
    task = asyncio.create_task(worker())
    await asyncio.sleep(1)
    task.cancel()                    # 发出取消
    try:
        await task                   # 等它真的停下
    except asyncio.CancelledError:
        print("已经停了")


asyncio.run(main())
# 干活中
# 干活中
# 干活中
# 被取消了，收尾
# 已经停了
```

超时其实就是「到点自动 cancel」，所以超时和取消走的是同一套机制。

### 限制同时跑几个：Semaphore（进阶）

`gather` 一下子开 100 个请求，对方服务器可能直接把你限流。用 `Semaphore`（信号量）控制最多同时跑几个：

```python
import asyncio
import time


async def fetch(i: int, sem: asyncio.Semaphore) -> int:
    async with sem:                  # 拿到名额才进去，最多 3 个同时在里面
        await asyncio.sleep(1)
        return i


async def main() -> None:
    sem = asyncio.Semaphore(3)
    start = time.perf_counter()
    results = await asyncio.gather(*(fetch(i, sem) for i in range(9)))
    print(results)                                     # [0, 1, 2, 3, 4, 5, 6, 7, 8]
    print(f"用时 {time.perf_counter() - start:.1f}s")    # 用时 3.0s：9 个任务，每次 3 个


asyncio.run(main())
```

### 其中一个出错了怎么办（进阶）

`gather` 里有一个任务抛错，`await gather(...)` 就会抛出这个错，其他任务的结果也拿不到。加上 `return_exceptions=True`，错误会和正常结果一起放进列表，自己挨个判断：

```python
import asyncio


async def job(n: int) -> int:
    if n == 2:
        raise ValueError("2 号失败")
    return n * 10


async def main() -> None:
    results = await asyncio.gather(job(1), job(2), job(3), return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            print("失败：", r)
        else:
            print("成功：", r)


asyncio.run(main())
# 成功： 10
# 失败： 2 号失败
# 成功： 30
```

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
    async with httpx.AsyncClient(base_url="https://httpbin.org", timeout=10) as client:
        start = time.perf_counter()
        for _ in range(3):                                # 一个一个发：等完一个再发下一个
            await client.get("/delay/1")
        print(f"一个一个发：{time.perf_counter() - start:.1f}s")

        start = time.perf_counter()
        # 循环 3 次准备 3 个请求（_ 表示循环变量用不到）；没 await，请求还没发出去
        # requests = [未发出的请求, 未发出的请求, 未发出的请求]
        requests = [client.get("/delay/1") for _ in range(3)]
        # *requests 把列表拆开传给 gather，等于 gather(请求1, 请求2, 请求3)：一起发出、一起等
        responses = await asyncio.gather(*requests)
        print([r.status_code for r in responses])
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
    for attempt in range(1, retries + 1):
        try:
            r = httpx.get(url, timeout=5)
            if r.status_code < 500 and r.status_code != 429:   # 成功，或者重试也没用的错误
                return r
            print(f"第 {attempt} 次：{r.status_code}")
        except httpx.TransportError as e:                       # 超时、连不上
            print(f"第 {attempt} 次：{type(e).__name__}")
        if attempt < retries:
            time.sleep(2 ** (attempt - 1))                      # 等 1 秒、2 秒……越来越久
    raise RuntimeError(f"重试 {retries} 次都失败了：{url}")


try:
    get_with_retry("https://httpbin.org/status/503")
except RuntimeError as e:
    print(e)
# 第 1 次：503
# 第 2 次：503
# 第 3 次：503
# 重试 3 次都失败了：https://httpbin.org/status/503
```

- **等待时间越来越长**（1、2、4 秒）叫指数退避：对方已经忙不过来了，大家还一起狂刷只会更糟。
- **次数要有上限**：一直失败就放弃，把错误报出来。
- 实际项目里可以用 `tenacity` 这类库，用装饰器写重试，原理和上面一样。

## 2.7 线程、进程、协程和 GIL {#concurrency}

「同时做好几件事」在 Python 里有三种办法。面试常问它们的区别，写代码时也要知道该用哪个。

### 三者的区别

| | 进程 | 线程 | 协程（async） |
|---|---|---|---|
| 是什么 | 一个独立运行的程序，有自己的内存 | 进程里的一条执行线路，同一个进程的线程共享内存 | 一个线程里的很多个任务，靠 `await` 主动让出 |
| 谁来切换 | 操作系统 | 操作系统（随时可能切走） | 自己：只在 `await` 的地方切换 |
| 开销 | 大（几十 MB 内存，启动慢） | 中 | 很小（开几万个都没问题） |
| 能不能多核一起算 | 能 | **不能**（因为 GIL，见下面） | 不能（只有一个线程） |
| 适合 | 大量计算 | 等待：网络、文件、数据库 | 大量等待：成百上千个网络请求 |

### GIL：为什么 Python 多线程不能一起算

GIL（全局解释器锁）是 CPython（就是我们平时用的 Python）里的一把锁：**同一时刻只有一个线程在执行 Python 代码**。所以开再多线程，纯计算的部分也是轮流跑，不会更快。

但线程在**等待**的时候（等网络、等磁盘、`time.sleep`）会把锁放开，别的线程可以接着跑。所以：

- **等待为主（IO 密集）**：多线程有用，等的时间能重叠起来。
- **计算为主（CPU 密集）**：多线程没用，要用多进程：每个进程有自己的 GIL，可以真正用上多个 CPU 核。

实际跑一下就知道了（这段要存成文件运行）：

```python
# cpu_demo.py
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def count(n: int) -> int:          # 纯计算：从 0 加到 n
    total = 0
    for i in range(n):
        total += i
    return total


def timed(label: str, run) -> None:
    start = time.perf_counter()
    run()
    print(f"{label}：{time.perf_counter() - start:.1f}s")


if __name__ == "__main__":          # 用多进程时必须写这一行
    jobs = [20_000_000] * 4

    timed("一个一个算", lambda: [count(n) for n in jobs])
    with ThreadPoolExecutor(max_workers=4) as pool:
        timed("4 个线程", lambda: list(pool.map(count, jobs)))
    with ProcessPoolExecutor(max_workers=4) as pool:
        timed("4 个进程", lambda: list(pool.map(count, jobs)))
```

```
一个一个算：1.2s
4 个线程：1.1s       ← 和一个一个算差不多：GIL 让线程只能轮流算
4 个进程：0.3s       ← 4 个核一起算，快了 4 倍
```

（具体秒数看电脑，比例差不多。）多进程必须写 `if __name__ == "__main__":`：新进程启动时会重新导入这个文件，不加这个判断，每个新进程又会去开新进程。

### 等待为主：线程池

同样是 5 个「等 1 秒」的任务，用线程池一起等，总共 1 秒：

```python
import time
from concurrent.futures import ThreadPoolExecutor


def wait_io(i: int) -> int:
    time.sleep(1)                   # 模拟等网络、等数据库
    return i


start = time.perf_counter()
with ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(wait_io, range(5)))
print(results)                                     # [0, 1, 2, 3, 4]
print(f"用时 {time.perf_counter() - start:.1f}s")    # 用时 1.0s，不是 5 秒
```

`pool.map(函数, 列表)` 把列表里每个值交给一个线程去调用这个函数，结果按原来的顺序返回。

### async 里要调用同步的慢函数：`asyncio.to_thread`

有些库只有同步版本（比如某些 SDK、文件处理），直接在 `async def` 里调用会卡住事件循环。用 `asyncio.to_thread` 把它放到线程里跑，`await` 等结果：

```python
import asyncio
import time


def slow_sync(name: str) -> str:    # 一个只有同步版本的慢函数
    time.sleep(1)
    return f"{name} 完成"


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(
        asyncio.to_thread(slow_sync, "A"),
        asyncio.to_thread(slow_sync, "B"),
    )
    print(results)                                     # ['A 完成', 'B 完成']
    print(f"用时 {time.perf_counter() - start:.1f}s")    # 用时 1.0s


asyncio.run(main())
```

### 怎么选

| 场景 | 用什么 |
|---|---|
| 写 FastAPI 接口，用的库支持 async（httpx、异步数据库驱动） | `async def` + `await` |
| 写 FastAPI 接口，用的库只有同步版本 | 普通 `def`，FastAPI 自动放到线程池里跑 |
| async 代码里临时要调一个同步的慢函数 | `asyncio.to_thread` |
| 脚本里要同时发一批请求、读一批文件 | 线程池，或者 async + `gather` |
| 大量计算：图片处理、数据分析 | 多进程（`ProcessPoolExecutor`） |
| 很重、很慢的后台任务（比如生成视频） | 交给单独的任务队列去跑，接口立刻返回（阶段六） |

> Python 3.13 起有一个实验性的「无 GIL」版本，以后线程也许能多核一起算，但现在大部分项目和库还是按有 GIL 来写的。

## 2.8 with 和上下文管理器 {#context-manager}

第 1.12 节用过 `with open(...)`：进入时拿到资源，离开时自动收尾，中途出错也会收尾。能放在 `with` 后面的对象叫**上下文管理器**。文件、httpx 的 `Client`、数据库会话、锁都是。

后端里到处都是这种「先准备、用完一定要收尾」的事：开数据库会话要关、开事务要提交或回滚、服务启动时建连接池、关闭时释放。这一节讲怎么自己写一个。

### 用 `@contextmanager` 写一个

最常用的写法：写一个带 `yield` 的函数，加上 `@contextmanager`。`yield` 前面是「进入时做的事」，后面是「离开时做的事」，`yield` 出去的值就是 `as` 拿到的东西。

```python
import time
from contextlib import contextmanager


@contextmanager
def timer(label: str):
    start = time.perf_counter()          # 进入 with 时执行
    try:
        yield                            # 在这里暂停，去执行 with 里面的代码
    finally:
        print(f"{label} 用了 {time.perf_counter() - start:.1f}s")   # 离开 with 时执行


with timer("睡一会"):
    time.sleep(0.5)
# 睡一会 用了 0.5s
```

`yield` 外面要包 `try / finally`：`with` 里面出了错，错误会从 `yield` 那一行抛出来，不写 `finally` 的话收尾代码就跳过了。

### 出错时做不同的事：事务

`yield` 外面也能用 `except`，出错时做一件事、没出错做另一件。数据库事务就是这个结构：全部成功才提交，有一步出错就回滚，然后把错误接着往外抛。

```python
from contextlib import contextmanager


class FakeDB:                            # 假装是一个数据库连接
    def commit(self) -> None:
        print("提交")

    def rollback(self) -> None:
        print("回滚")

    def close(self) -> None:
        print("关闭连接")


@contextmanager
def transaction():
    db = FakeDB()
    try:
        yield db                         # as 拿到的就是 db
        db.commit()                      # with 里没出错才走到这里
    except Exception:
        db.rollback()
        raise                            # 回滚完接着抛，不能把错误吞掉
    finally:
        db.close()


with transaction() as db:
    print("写入两条数据")
# 写入两条数据
# 提交
# 关闭连接

try:
    with transaction() as db:
        print("写入第一条")
        raise ValueError("第二条数据不对")
except ValueError as e:
    print("出错了：", e)
# 写入第一条
# 回滚
# 关闭连接
# 出错了： 第二条数据不对
```

SQLAlchemy 的 `with session.begin():` 做的就是这件事。

### 用类写：`__enter__` 和 `__exit__`

`@contextmanager` 背后就是这两个方法：进入 `with` 时调用 `__enter__`，它的返回值给 `as`；离开时调用 `__exit__`。库的源码里常见这种写法，能看懂就行，自己写一般用 `@contextmanager`。

```python
import time


class Timer:
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self                      # 给 as

    def __exit__(self, exc_type, exc, tb) -> None:   # 出错时三个参数是错误信息，没出错都是 None
        self.seconds = time.perf_counter() - self.start


with Timer() as t:
    time.sleep(0.2)
print(f"{t.seconds:.1f}s")    # 0.2s
```

### 一次开好几个

```python
with open("a.txt", encoding="utf-8") as src, open("b.txt", "w", encoding="utf-8") as dst:
    dst.write(src.read())    # 两个文件都会自动关
```

### async 版本：`async with` 和 `@asynccontextmanager`

进入、离开时要 `await` 的（异步建连接、异步关闭），用 `async with`，第 2.5、2.6 节的 `asyncio.timeout`、`httpx.AsyncClient` 都是。自己写就把 `@contextmanager` 换成 `@asynccontextmanager`，函数改成 `async def`。

FastAPI 的 `lifespan` 就是这么写的：`yield` 之前是服务启动时做的事，之后是服务关闭时做的事。

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

第 3.8 节依赖注入里带 `yield` 的 `get_session`，也是同一个思路：`yield` 前开会话，`yield` 后关会话，只是由 FastAPI 在每个请求前后替你执行。

---

# 阶段三：FastAPI 后端开发

做一个 todo 接口项目：用 FastAPI 写接口，先手写 SQL 打基础，再用 SQLAlchemy 把数据存进 SQLite，pytest 写测试（3.1～3.10）；再一步步升级成能上线的多用户后端：拆文件、注册登录、数据隔离和分页、数据库迁移、部署（3.11～3.15）。

## 3.1 项目准备 {#project-setup}

```bash
mkdir -p todo-api/app todo-api/tests && cd todo-api
touch app/__init__.py tests/__init__.py
uv pip install fastapi "uvicorn[standard]" sqlalchemy pytest httpx python-dotenv
```

- `__init__.py`：空文件，让 `app`、`tests` 成为包，才能写 `from app.db import ...`。
- 已经在上一级激活过 `.venv` 就不用再建虚拟环境，包装进同一个 `.venv` 就行。

| 包 | 作用 |
|---|---|
| fastapi | 写接口的框架 |
| uvicorn | 运行接口的服务器 |
| sqlalchemy | 用 Python 类操作数据库 |
| pytest | 跑测试 |
| httpx | 测试里的 `TestClient` 要用它 |
| python-dotenv | 启动时读取 `.env` 文件里的配置（第 3.6 节） |

`"uvicorn[standard]"` 要加引号，否则 zsh 会把方括号当通配符。

最后的目录结构：

```
todo-api/
├── app/
│   ├── __init__.py
│   ├── db.py          # 连数据库、会话
│   ├── models.py      # 表定义
│   ├── schemas.py     # 请求 / 响应的数据格式
│   ├── errors.py      # 统一响应格式和错误
│   └── main.py        # 接口
└── tests/
    ├── __init__.py
    └── test_tasks.py
```

## 3.2 第一个接口 {#first-api}

```python
# app/hello.py
from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    age: int


@app.get("/users")                      # 列表：查询参数 /users?q=tom&page=2
def list_users(q: str | None = None, page: int = 1) -> dict:
    return {"q": q, "page": page}


@app.get("/users/{user_id}")            # 详情：路径参数 /users/5
def get_user(user_id: int) -> dict:
    return {"user_id": user_id}


@app.post("/users", status_code=201)    # 新建：请求体 {"name": "Tom", "age": 18}
def create_user(body: User) -> dict:
    return {"created": body.model_dump()}


@app.put("/users/{user_id}")            # 修改：路径参数 + 请求体
def update_user(user_id: int, body: User) -> dict:
    return {"user_id": user_id, "updated": body.model_dump()}


@app.delete("/users/{user_id}")         # 删除：路径参数
def delete_user(user_id: int) -> dict:
    return {"deleted": user_id}


@app.get("/me")                         # 请求头：X-Token: abc
def me(x_token: Annotated[str, Header()]) -> dict:
    return {"token": x_token}
```

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

- 有默认值是可选，没默认值是必填；必填的没传，或者类型不对（比如 `/users/abc`），自动返回 422。
- RESTful：路径用名词复数表示资源，动作用 HTTP 方法表示，不写 `/getUser`、`/users/list` 这种。
- 固定路径要写在 `{参数}` 路径前面，比如 `/users/me` 要写在 `/users/{user_id}` 前面，否则 `me` 会被当成 `user_id`。

## 3.3 请求体和响应：pydantic {#pydantic}

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
    model_config = ConfigDict(from_attributes=True)   # 允许直接从对象的属性读值（第 3.9 节用）

    id: int
    title: str
    done: bool
    note: str | None          # 没有默认值：必须给，但可以是 None
    created_at: datetime      # 输出 JSON 时自动转成 ISO 字符串
    updated_at: datetime


class TaskList(BaseModel):
    items: list[TaskOut]      # 模型可以嵌套
    total: int
```

```python
TaskCreate(title="写笔记")          # ✅
TaskCreate(title="")                # ❌ ValidationError：至少 1 个字符
TaskCreate(title="a").model_dump()  # {'title': 'a', 'note': None}  转成 dict
```

**`from_attributes=True`**：`TaskOut` 加了这个配置后，可以用 `TaskOut.model_validate(对象)` 直接从一个对象上按字段名读取同名属性来创建，不用一个个字段手写 `TaskOut(id=task.id, title=task.title, ...)`。第 3.9 节就用它把数据库里的 `Task` 转成返回给前端的 `TaskOut`。

在接口里，参数类型写成 `TaskCreate`，FastAPI 就从请求体读 JSON、校验，不通过自动返回 422，函数根本不会执行：

```python
@app.post("/tasks")
def create_task(body: TaskCreate) -> dict:
    print(body.title, body.note)     # 已经校验好，直接用点号取值
    ...
```

**常用写法**：

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

## 3.4 统一响应和错误处理 {#errors}

**约定**：HTTP 状态码照实返回；响应体统一是 `{code, msg, data}`。

| 情况 | HTTP 状态码 | 响应体 |
|---|---|---|
| 成功 | 200、201 | `{"code": 200, "msg": "ok", "data": 数据}` |
| 失败 | 404、409…… | `{"code": -1, "msg": "提示文字", "data": null}` |

接口里只有一条规矩：**成功就 `return success(...)`，失败就 `raise fail(...)`**。

```python
# app/errors.py
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status: int, msg: str) -> None:
        super().__init__(msg)    # 打印这个异常时显示 msg
        self.status = status     # HTTP 状态码：404、409……
        self.msg = msg           # 给用户看的提示


# 1. 成功：return success(数据)
def success(data: object = None, msg: str = "ok") -> dict:
    return {"code": 200, "msg": msg, "data": data}


# 2. 失败：raise fail(状态码, 提示)
def fail(status: int, msg: str) -> ApiError:
    return ApiError(status, msg)


# 常用的错误写成函数，各处直接 raise task_not_found()
def task_not_found() -> ApiError:
    return fail(404, "没有这个任务")


# 3. 统一的错误处理器：任何接口抛出 ApiError，都由这里转成 JSON 响应
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

在 `main.py` 里创建 app 之后调用一次：`errors.install(app)`。

- **`success(data, msg)`**：成功时把数据包一层。`success(task)` 得到 `{"code": 200, "msg": "ok", "data": task}`；`success(msg="删除成功")` 得到 `{"code": 200, "msg": "删除成功", "data": null}`。
- **`fail(status, msg)`**：生成一个错误，前面要加 `raise` 才会抛出去：`raise fail(409, "已经有同名任务了")`。
- **为什么失败用 `raise` 而不是 `return`**：`raise` 会让函数立刻停下，而且不管嵌套几层都能直接抛到 FastAPI。比如第 3.9 节的 `load_task()` 是被接口调用的普通函数，它在里面 `raise task_not_found()`，接口不用再判断一次返回值。
- **`install()`**：启动时向 FastAPI 登记「遇到 `ApiError`，就调用 `handle_api_error` 生成 `{code: -1, msg, data: null}`」。`ApiError` 是 `fail()` 背后真正被抛出的异常类，接口里不用直接写它。

**出错时代码怎么走**（以 `GET /tasks/99` 为例）：

1. 接口里执行 `raise task_not_found()`，函数立即中断。
2. 异常往外抛，被 FastAPI 接住。
3. FastAPI 发现是 `ApiError`，调用启动时登记的 `handle_api_error`。
4. 返回 404 和 `{"code": -1, "msg": "没有这个任务", "data": null}`。

**先动手试**（不连数据库）：

```python
# errors_demo.py（放在 todo-api/ 下）
from fastapi import FastAPI

from app import errors
from app.errors import fail, success, task_not_found

app = FastAPI()
errors.install(app)

TASKS = {1: "写笔记"}          # 先用 dict 假装数据库


@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    if task_id not in TASKS:
        raise task_not_found()
    return success({"id": task_id, "title": TASKS[task_id]})


@app.post("/tasks", status_code=201)
def create_task(title: str) -> dict:
    if title in TASKS.values():
        raise fail(409, "已经有同名任务了")
    new_id = max(TASKS) + 1
    TASKS[new_id] = title
    return success({"id": new_id, "title": title}, msg="创建成功")
```

`uvicorn errors_demo:app --reload` 启动，实际结果：

| 请求 | HTTP | 响应体 |
|---|---|---|
| `GET /tasks/1` | 200 | `{"code": 200, "msg": "ok", "data": {"id": 1, "title": "写笔记"}}` |
| `GET /tasks/99` | 404 | `{"code": -1, "msg": "没有这个任务", "data": null}` |
| `POST /tasks?title=写笔记` | 409 | `{"code": -1, "msg": "已经有同名任务了", "data": null}` |
| `POST /tasks?title=读书` | 201 | `{"code": 200, "msg": "创建成功", "data": {"id": 2, "title": "读书"}}` |

### 完整的错误拦截

上面的 `install()` 只拦截了 `ApiError`。下面这些错误不是你 `raise fail(...)` 抛的，而是 FastAPI 自己发现的，所以不会经过 `handle_api_error`，返回的还是 FastAPI 的默认格式：

| 情况 | 默认返回 |
|---|---|
| 参数校验失败（缺字段、类型不对） | 422 `{"detail": [{"type": ..., "loc": [...], "msg": ...}]}` |
| 路径不存在、请求方法不对 | 404 `{"detail": "Not Found"}` / 405 `{"detail": "Method Not Allowed"}` |
| 代码 bug | 500 纯文本 `Internal Server Error`，不是 JSON |

前端按约定读 `res.msg` 时，这几种情况都会拿到 `undefined`。所以正式项目里，会在 `install()` 里把这几种错误也拦截下来，统一成 `{code, msg, data}`。把 `app/errors.py` 换成下面的完整版：

```python
# app/errors.py（完整版）
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    def __init__(self, status: int, msg: str) -> None:
        super().__init__(msg)
        self.status = status
        self.msg = msg


def success(data: object = None, msg: str = "ok") -> dict:
    return {"code": 200, "msg": msg, "data": data}


def fail(status: int, msg: str) -> ApiError:
    return ApiError(status, msg)


def task_not_found() -> ApiError:
    return fail(404, "没有这个任务")


def error_response(status: int, msg: str) -> JSONResponse:
    """所有错误都用这一个格式返回。"""
    return JSONResponse(status_code=status, content={"code": -1, "msg": msg, "data": None})


def install(app: FastAPI) -> None:
    """统一的错误拦截：不管哪种错误，前端收到的都是 {code: -1, msg, data: null}。"""

    # ① 业务错误：接口里 raise fail(...)
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        return error_response(exc.status, exc.msg)

    # ② 参数校验失败：缺字段、类型不对、长度超限……
    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]           # 可能有好几条，只取第一条
        field = first["loc"][-1]          # 出错的位置，如 ["body", "title"]，取最后一个 → "title"
        return error_response(422, f"{field}：{first['msg']}")

    # ③ 框架报的 HTTP 错误：路径不存在 404、请求方法不对 405
    @app.exception_handler(StarletteHTTPException)
    async def handle_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        msgs = {404: "没有这个接口", 405: "这个接口不支持这种请求方式"}
        return error_response(exc.status_code, msgs.get(exc.status_code, str(exc.detail)))

    # ④ 兜底：上面都没接住的异常，基本就是代码 bug
    @app.exception_handler(Exception)
    async def handle_unknown(request: Request, exc: Exception) -> JSONResponse:
        # 完整的报错堆栈 uvicorn 会打印在终端里，这里不把细节给前端
        return error_response(500, "服务出错了，请稍后再试")
```

- **4 个处理器**：FastAPI 根据异常的类型，交给对应的处理器。`ApiError` 也是 `Exception` 的子类，但它有专门的 ①，所以走 ①；只有前面三个都没接住的异常，才会落到兜底的 ④。
- **`error_response()`**：4 个处理器都用它返回，保证格式完全一样。
- **② 里的 `first["loc"]`**：出错的位置，比如 `["body", "title"]`、`["path", "task_id"]`、`["query", "page"]`，最后一个元素就是字段名。
- **④ 不把报错细节给前端**：报错信息里可能有代码路径、SQL 语句等内部细节。前端只拿到一句通用提示，完整报错去运行 uvicorn 的终端里看。
- 用 FastAPI 自带的 `raise HTTPException(404, ...)` 抛出的错误，也会被 ③ 接住。

在 `errors_demo.py` 末尾临时加一个会出错的接口，用来试 ④：

```python
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

参数校验失败用 422 还是 400，团队统一就行，很多项目用 400。如果改成 400，第 3.10 节测试里 `test_empty_title_rejected` 的 422 也要跟着改。

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

## 3.5 SQL 基础：PostgreSQL {#sql-basics}

下一节开始用 SQLAlchemy 操作数据库，写的是 Python，但发给数据库的还是 SQL。这一节先不碰 Python，直接在数据库里手写 SQL：建表、增删改查、关联、统计、索引、事务。会了这些，看 SQLAlchemy 打印出来的 SQL、排查慢查询、写统计报表都用得上。

数据库用 **PostgreSQL**（简称 Postgres）：第 3.15 节部署用的 Neon 就是 Postgres，本地和线上用同一种最省事。最后对比一下它和 MySQL 的区别。

### 装好、连上

```bash
brew install postgresql@17          # Mac；Windows 去官网下载安装包
brew services start postgresql@17   # 后台启动，开机自动运行
createdb learn                      # 建一个练习用的库
psql learn                          # 进入命令行，之后的 SQL 都在这里敲
```

不想装的话，用 Neon 免费版建一个库，复制它给的连接地址，`psql "postgresql://..."` 一样能连。

psql 里几个常用命令（不是 SQL，不用分号）：

| 命令 | 作用 |
|---|---|
| `\dt` | 列出所有表 |
| `\d tasks` | 看 `tasks` 的列、索引、外键 |
| `\di` | 列出所有索引 |
| `\x` | 切换竖着显示（列多时好看） |
| `\q` | 退出 |

SQL 语句以分号结尾，没写分号直接回车，psql 会等你继续输入。关键字大小写都行，习惯写大写。

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
    created_at timestamptz NOT NULL DEFAULT now()
);
```

- `--` 后面是注释。
- **主键** `PRIMARY KEY`：每行的唯一编号，不能重复、不能为空。`serial` 是「整数 + 自动加一」。
- **约束**：`NOT NULL`、`UNIQUE`、`REFERENCES` 都是数据库替你把关，不合规的数据直接拒绝写入，比只在代码里检查可靠。
- **外键** `REFERENCES users(id)`：`tasks.user_id` 必须是 `users` 里存在的 id。`ON DELETE CASCADE`：删用户时，他的任务一起删掉。
- `timestamptz` 是带时区的时间，存的是一个绝对时刻，Postgres 里存时间优先用它。

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
UPDATE tasks SET done = true WHERE id = 1;

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
-- JOIN：两边都对得上的才出现。t、u 是表的简写
SELECT u.username, t.title, t.done
FROM tasks t
JOIN users u ON u.id = t.user_id
ORDER BY t.id;
--  username | title  | done
-- ----------+--------+------
--  alice    | 写笔记 | t
--  alice    | 学 SQL | f
--  bob      | 买菜   | f

-- LEFT JOIN：左边的表全保留，右边对不上的填 NULL
SELECT u.username, t.title
FROM users u
LEFT JOIN tasks t ON t.user_id = u.id
ORDER BY u.id, t.id;
--  username | title
-- ----------+--------
--  alice    | 写笔记
--  alice    | 学 SQL
--  bob      | 买菜
--  carol    |            ← carol 没有任务，title 是 NULL
```

「列出所有用户，包括还没数据的」就用 `LEFT JOIN`，用 `JOIN` 会把 carol 漏掉。

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
EXPLAIN ANALYZE SELECT id, title FROM tasks WHERE title = '任务 299999';
--  Parallel Seq Scan on tasks ...
--    Rows Removed by Filter: 150001
--  Execution Time: 7.625 ms

CREATE INDEX idx_tasks_title ON tasks (title);

EXPLAIN ANALYZE SELECT id, title FROM tasks WHERE title = '任务 299999';
--  Index Scan using idx_tasks_title on tasks ...
--  Execution Time: 0.023 ms
```

- `Seq Scan` 是全表扫描，`Index Scan` 是走索引。同一条查询从 7.6 毫秒变成 0.02 毫秒，数据越多差得越多。
- 主键和 `UNIQUE` 会自动建索引（`\di` 能看到 `users_username_key`）。**Postgres 不会给外键自动建索引**，`tasks.user_id` 经常拿来筛选，要自己建：`CREATE INDEX ON tasks (user_id);`。
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
- 转账这类「扣 A 的钱、加 B 的钱」必须放在一个事务里，中间出错就回滚，不会出现只扣不加。第 2.8 节 `with` 里的 `commit` / `rollback`、SQLAlchemy 的 `session.commit()`，背后都是这个。
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
- 用 SQLAlchemy 时，大部分差异被它屏蔽了，换库主要是换连接地址（第 3.14 节有实操）。两个都会一点最好，会了 Postgres 再学 MySQL 很快。

### 下一节：SQL 交给 SQLAlchemy 写

上面的 SQL，到了 Python 里会变成这样：

| SQL | SQLAlchemy（下一节开始讲） |
|---|---|
| `CREATE TABLE tasks (...)` | `class Task(Base)` 加 `Base.metadata.create_all(engine)` |
| `INSERT INTO tasks ...` | `session.add(Task(title=...))` |
| `SELECT ... WHERE done = false` | `select(Task).where(Task.done == False)` |
| `COMMIT` / `ROLLBACK` | `session.commit()` / `session.rollback()` |

练习项目先用 SQLite：一个文件就是一个库，不用装服务。练完把连接地址换成 Postgres，代码基本不用改。

## 3.6 连数据库：SQLAlchemy {#sqlalchemy}

**一个类 = 一张表，一个对象 = 一行，一个属性 = 一列。**

**先把配置放进 `.env`**：数据库地址这类配置不写死在代码里。在 `todo-api/` 下新建 `.env`：

```
DATABASE_URL=sqlite:///todo.db
```

`.env` 里以后会有密码，**不能提交**，要写进 `.gitignore`。另外建一个 `.env.example` 提交上去，只写有哪些配置、不写真实的值，别人复制一份改名成 `.env` 就能用：

```
DATABASE_URL=sqlite:///todo.db
```

```python
# app/db.py
from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()      # 读当前目录的 .env，把里面的配置放进环境变量（已经设置过的不覆盖）

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///todo.db")   # 读环境变量，读不到用默认值

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

**`DATABASE_URL` 是怎么读到的**：

```
.env 文件里的一行  DATABASE_URL=sqlite:///todo.db
   ↓  load_dotenv()                     启动时把 .env 读进环境变量
环境变量 DATABASE_URL
   ↓  os.environ.get("DATABASE_URL")    读出来
create_engine(DATABASE_URL)             连上数据库
```

- `os.environ` 只能读到环境变量，不会自己去读 `.env`，所以要先 `load_dotenv()`。
- `load_dotenv()` 不覆盖已经设置过的环境变量：终端里 `export DATABASE_URL=...` 了，就以终端为准；线上服务器没有 `.env` 文件，直接设置环境变量就行，代码不用改。
- 不想在代码里加载，也可以在启动时让 uv 加载：`uv run --env-file .env uvicorn app.main:app --reload`。
- `sqlite:///todo.db` 是当前目录下的 `todo.db` 文件；换成 PostgreSQL 只要改这一行，比如 `postgresql+psycopg://用户:密码@localhost:5432/todo`。

**表定义里的几个点**：

- `Mapped[类型]`：Python 里这一列是什么类型。
- `mapped_column(...)`：数据库里这一列的定义。
- `default=_now`：插入时没给值，就调用 `_now()`。注意传的是函数本身，不加括号；写成 `default=datetime.now(UTC)` 会在程序启动时就算好一个固定时间，所有数据都一样。
- `onupdate=_now`：这一行被修改、提交时，自动调用 `_now()` 更新这一列。`updated_at` 就靠它：新建时和创建时间基本一样（各调一次 `_now()`，可能差几微秒），之后每次改动都会刷新。
- **表结构改了要删库重建**：`create_all` 只会建不存在的表，不会给已有的表加列。已经跑过旧版本的话，先删掉 `todo.db` 再启动，否则会报 `no such column: tasks.updated_at`。正式项目用 alembic 处理这种改动（第 3.14 节）。

## 3.7 增删改查：Session {#session}

**Session** 是你和数据库之间的一次「会话」：在里面查、加、改、删数据，它会记住你改了什么，等你 `commit()` 时一次性写进数据库。

- **增删改**：`session.add(...)`、改属性、`session.delete(...)` 都只是先记下来，**`commit()` 才真正写进数据库**。没 commit 就关闭会话，改动全部作废。
- **查**：`session.get(...)`、`session.scalars(...)` 会立即查数据库，把结果变成 `Task` 对象。查询不改数据，所以不用 commit。

下面每个接口演示一种操作。每个接口都用 `with SessionLocal() as session:` 开一个会话，`with` 结束自动关闭：

```python
# crud_demo.py（放在 todo-api/ 下）：每个接口演示一种数据库操作
from fastapi import FastAPI
from sqlalchemy import func, select

from app import errors
from app.db import Base, SessionLocal, engine
from app.errors import fail, success
from app.models import Task

app = FastAPI()
errors.install(app)
Base.metadata.create_all(engine)           # 建表（表已存在就跳过）


def to_dict(task: Task) -> dict:
    """数据库对象 → 返回给前端的 dict。"""
    return {"id": task.id, "title": task.title, "done": task.done, "note": task.note}


# 增：POST /tasks?title=写笔记
@app.post("/tasks", status_code=201)
def create_task(title: str, note: str | None = None) -> dict:
    with SessionLocal() as session:        # 开一个会话，with 结束自动关闭
        # 先查一条：同名的有没有，没有就是 None
        same = session.scalars(select(Task).where(Task.title == title)).one_or_none()
        if same is not None:
            raise fail(409, "已经有同名任务了")

        task = Task(title=title, note=note)
        session.add(task)                  # 只是记下「要插入」，还没写进数据库
        session.commit()                   # 真正写进数据库，task.id 这时有值了
        return success(to_dict(task), msg="创建成功")


# 查列表：GET /tasks?done=false
@app.get("/tasks")
def list_tasks(done: bool | None = None) -> dict:
    with SessionLocal() as session:
        stmt = select(Task).order_by(Task.id.desc())     # 按 id 倒序
        if done is not None:
            stmt = stmt.where(Task.done == done)          # 可以一步步加条件
        tasks = session.scalars(stmt).all()               # 执行查询，拿到对象列表
        total = session.scalar(select(func.count()).select_from(Task))   # 计数，只取一个值
        return success({"items": [to_dict(t) for t in tasks], "total": total})


# 查一条：GET /tasks/1
@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    with SessionLocal() as session:
        task = session.get(Task, task_id)                 # 按主键查，没有就是 None
        if task is None:
            raise fail(404, "没有这个任务")
        return success(to_dict(task))


# 改：PATCH /tasks/1/done
@app.patch("/tasks/{task_id}/done")
def finish_task(task_id: int) -> dict:
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if task is None:
            raise fail(404, "没有这个任务")
        task.done = True                   # 直接改属性，还没写进数据库
        session.commit()                   # commit 时自动生成 UPDATE
        return success(to_dict(task), msg="已完成")


# 删：DELETE /tasks/1
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> dict:
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if task is None:
            raise fail(404, "没有这个任务")
        session.delete(task)               # 记下「要删除」
        session.commit()                   # commit 时生成 DELETE
        return success(msg="删除成功")
```

在 `todo-api/` 目录启动，到 `/docs` 里按顺序试：

```bash
uvicorn crud_demo:app --reload
```

实际运行结果（按顺序执行）：

| 请求 | HTTP | 返回的 data / msg |
|---|---|---|
| `POST /tasks?title=写笔记` | 201 | `{"id": 1, "title": "写笔记", "done": false, "note": null}` |
| `POST /tasks?title=读书` | 201 | `{"id": 2, "title": "读书", ...}` |
| `POST /tasks?title=跑步&note=5 公里` | 201 | `{"id": 3, "title": "跑步", "note": "5 公里", ...}` |
| `POST /tasks?title=读书` | 409 | 已经有同名任务了 |
| `GET /tasks` | 200 | 3 条，id 倒序：跑步、读书、写笔记；`total: 3` |
| `GET /tasks/1` | 200 | `{"id": 1, "title": "写笔记", ...}` |
| `GET /tasks/99` | 404 | 没有这个任务 |
| `PATCH /tasks/1/done` | 200 | `{"id": 1, "done": true, ...}` |
| `GET /tasks?done=false` | 200 | 只剩跑步、读书 |
| `DELETE /tasks/2` | 200 | 删除成功 |
| `GET /tasks` | 200 | 剩跑步、写笔记，`total: 2` |

数据存在 `todo.db` 里，重启服务数据还在；想清空就删掉 `todo.db`。

**常用写法**：

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

想看 SQLAlchemy 实际发了什么 SQL：在 `db.py` 里改成 `create_engine(DATABASE_URL, echo=True)`，终端会打印每一条 SQL。你会看到 `add` 和改属性时什么都没发，`commit` 时才出现 `INSERT` / `UPDATE` / `DELETE`。

**发现问题了吗**：每个接口都在重复 `with SessionLocal() as session:`、查不到就 `raise fail(404, ...)`。下一节用依赖注入把「开会话」交给 FastAPI，第 3.9 节再把「查不到就 404」抽成 `load_task()`。

## 3.8 依赖注入：拿到数据库会话 {#dependency-injection}

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
        session.commit()       # ② 接口正常返回后，从这里继续
    except BaseException:
        session.rollback()     # ③ 接口抛了异常，撤销这次请求的所有修改
        raise
    finally:
        session.close()        # ④ 不管怎样都关闭


Db = Annotated[Session, Depends(db_session)]   # 起个短名字，接口里写 session: Db 就行
```

接口里使用：

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Db) -> dict:
    ...   # session 已经准备好了，直接用
```

- **`yield`**：函数执行到 `yield` 时交出一个值并暂停，之后从暂停的地方接着跑。执行顺序：① → 接口函数 → ② 或 ③ → ④。
- **`Annotated[Session, Depends(db_session)]`**：「类型是 Session，值由 `db_session` 提供」。
- **写接口里自己 `session.commit()`**：② 可能在响应已经发出去之后才执行，万一提交失败，前端会以为成功了。所以写数据的接口在返回前自己提交。

## 3.9 完整的 todo 接口 {#todo-api}

| 方法 | 路径 | 作用 | 成功时 |
|---|---|---|---|
| GET | `/tasks?done=false&limit=20` | 列表，可按是否完成筛选 | 200 |
| POST | `/tasks` | 新建；同名未完成任务已存在则 409 | 201 |
| GET | `/tasks/{id}` | 详情；不存在则 404 | 200 |
| PATCH | `/tasks/{id}/done` | 标记完成 | 200 |
| DELETE | `/tasks/{id}` | 删除 | 200 |

```python
# app/main.py
from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import errors
from app.db import Base, Db, engine
from app.errors import fail, success, task_not_found
from app.models import Task
from app.schemas import TaskCreate, TaskList, TaskOut

app = FastAPI(title="todo-api")
errors.install(app)
Base.metadata.create_all(engine)   # 练习用：启动时自动建表；正式项目用 alembic 管理表结构（第 3.14 节）


def load_task(session: Session, task_id: int) -> Task:
    """按 id 取任务，没有就报 404。好几个接口都要用，抽成函数。"""
    task = session.get(Task, task_id)
    if task is None:
        raise task_not_found()
    return task


@app.get("/tasks")
def list_tasks(session: Db, done: bool | None = None, limit: int = 20) -> dict:
    stmt = select(Task).order_by(Task.id.desc()).limit(limit)
    if done is not None:
        stmt = stmt.where(Task.done == done)     # 查询可以一步步加条件
    tasks = session.scalars(stmt).all()
    total = session.scalar(select(func.count()).select_from(Task))
    items = [TaskOut.model_validate(t) for t in tasks]   # 数据库对象 → 响应格式
    return success(TaskList(items=items, total=total or 0))


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate, session: Db) -> dict:
    if session.scalar(select(Task).where(Task.title == body.title, Task.done.is_(False))):
        raise fail(409, "已经有一条同名的未完成任务")
    task = Task(title=body.title, note=body.note)
    session.add(task)
    session.commit()         # 写接口自己提交：提交失败就报错，不会被当成成功
    return success(TaskOut.model_validate(task), msg="创建成功")


@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Db) -> dict:
    return success(TaskOut.model_validate(load_task(session, task_id)))


@app.patch("/tasks/{task_id}/done")
def finish_task(task_id: int, session: Db) -> dict:
    task = load_task(session, task_id)
    task.done = True         # 改属性就行，提交时自动生成 UPDATE
    session.commit()
    return success(TaskOut.model_validate(task))


# 删除成功返回 200 而不是 204：204 表示「没有响应体」，而我们约定每个响应都有 {code, msg, data}
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Db) -> dict:
    session.delete(load_task(session, task_id))
    session.commit()
    return success(msg="删除成功")
```

- **`TaskOut.model_validate(task)`**：把数据库里的 `Task` 对象转成返回给前端的 `TaskOut`（第 3.3 节加了 `from_attributes=True` 才能这样用）。
- **为什么不能直接 `success(task)`**：`Task` 是 SQLAlchemy 的数据库对象，FastAPI 不知道怎么把它转成 JSON，会报错返回 500。转成 `TaskOut` 还有一个好处：只输出 `TaskOut` 里定义的字段，以后表里加了不该给前端看的列，也不会被带出去。

启动：`uvicorn app.main:app --reload`，到 `/docs` 里点着试，或者用 curl：

```bash
curl -X POST http://127.0.0.1:8000/tasks -H 'Content-Type: application/json' -d '{"title": "写笔记"}'
curl http://127.0.0.1:8000/tasks
curl -X PATCH http://127.0.0.1:8000/tasks/1/done
curl -i http://127.0.0.1:8000/tasks/99      # -i 显示状态码：404 + {"code": -1, "msg": "没有这个任务", "data": null}
```

## 3.10 写测试：pytest {#pytest}

`TestClient` 不用启动服务，就能在代码里对 app 发请求。pytest 自动找 `test_` 开头的文件和函数来跑。

```python
# tests/test_tasks.py
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, db_session
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    # 每个测试一个全新的内存库，测试之间互不影响
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(engine, autoflush=False, expire_on_commit=False)

    def test_db_session() -> Iterator[Session]:
        session = TestSession()
        try:
            yield session
            session.commit()
        finally:
            session.close()

    app.dependency_overrides[db_session] = test_db_session   # 把真库换成测试库
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_and_list(client: TestClient) -> None:
    r = client.post("/tasks", json={"title": "写笔记"})
    assert r.status_code == 201
    assert r.json()["code"] == 200
    assert r.json()["data"]["title"] == "写笔记"
    assert r.json()["data"]["done"] is False

    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json()["data"]["total"] == 1
    assert [t["title"] for t in r.json()["data"]["items"]] == ["写笔记"]


def test_empty_title_rejected(client: TestClient) -> None:
    r = client.post("/tasks", json={"title": ""})
    assert r.status_code == 422


def test_duplicate_title_conflict(client: TestClient) -> None:
    client.post("/tasks", json={"title": "写笔记"})
    r = client.post("/tasks", json={"title": "写笔记"})
    assert r.status_code == 409
    assert r.json() == {"code": -1, "msg": "已经有一条同名的未完成任务", "data": None}


def test_finish_and_filter(client: TestClient) -> None:
    a = client.post("/tasks", json={"title": "a"}).json()["data"]["id"]
    client.post("/tasks", json={"title": "b"})
    assert client.patch(f"/tasks/{a}/done").json()["data"]["done"] is True
    items = client.get("/tasks", params={"done": False}).json()["data"]["items"]
    assert [t["title"] for t in items] == ["b"]


def test_delete_then_404(client: TestClient) -> None:
    task_id = client.post("/tasks", json={"title": "a"}).json()["data"]["id"]
    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["msg"] == "删除成功"
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 404
    assert r.json() == {"code": -1, "msg": "没有这个任务", "data": None}
```

在 `todo-api/` 目录运行：

```bash
python -m pytest -q            # 应该看到 5 passed
python -m pytest -q -k 404     # 只跑名字里带 404 的测试
```

- **`assert 条件`**：条件不成立就算失败，pytest 会把两边的实际值打印出来。
- **`@pytest.fixture`**：测试的准备工作。测试函数参数里写了 `client`，pytest 就先跑同名的 fixture，把 `yield` 出来的东西传进去；测试结束后执行 `yield` 后面的收尾。
- **`app.dependency_overrides`**：测试时把某个依赖换掉，这里把真数据库换成内存库，跑完不留垃圾。
- 内存库 `sqlite://` 要配 `StaticPool`，否则每个连接拿到的都是一个新的空库，会报 `no such table`。

## 3.11 拆文件和配置 {#routers-settings}

到 3.10 为止，所有接口都写在 `main.py` 里。接下来要加注册登录，接口会越来越多，先把结构理顺：**按业务拆成多个路由文件，配置集中到一个地方**。这一节只搬代码、不改功能，搬完 3.10 的测试应该原样通过。

```bash
uv pip install pydantic-settings
```

拆完的目录（后面几节在这个基础上加文件）：

```
todo-api/
├── app/
│   ├── config.py          # 新增：所有配置
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── errors.py
│   ├── routers/           # 新增：按业务分的接口
│   │   ├── __init__.py
│   │   └── tasks.py       # /tasks 相关的接口
│   └── main.py            # 只负责创建 app、把路由挂上去
└── tests/
```

### 配置：pydantic-settings

3.6 节用 `load_dotenv()` + `os.environ.get(...)` 读配置。配置一多就有问题：读出来全是字符串，要自己转类型；同一个配置在好几个文件里各读一遍，默认值还可能写得不一样。

`pydantic-settings` 用写 pydantic 模型的方式定义配置：字段名就是环境变量名，类型自动转换、校验，不对就启动失败。

```python
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """所有配置都在这里：先读环境变量，没有再读 .env，都没有用默认值。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///todo.db"   # 对应环境变量 DATABASE_URL（不区分大小写）
    debug: bool = False                       # DEBUG=true 会自动转成 True


settings = Settings()   # 整个项目共用这一个，别处 from app.config import settings
```

- **读取顺序**：环境变量 → `.env` 文件 → 默认值。线上直接设环境变量，本地写 `.env`，代码不用改，和 3.6 节一样。
- **自动转类型**：`DEBUG=true` 读进来就是 `True`，写成 `DEBUG=abc` 启动直接报错，不会带着错误的配置跑起来。
- **`extra="ignore"`**：`.env` 里有这个类没定义的配置（比如给别的工具用的），忽略，不报错。

`app/db.py` 开头改成从 `settings` 读，`load_dotenv` 和 `os` 都不用了：

```python
# app/db.py（开头改成这样，后面不变）
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, echo=settings.debug)   # debug 时打印每条 SQL
```

### 拆路由：APIRouter

`APIRouter` 是「一组接口」，写法和 `app` 一样（`@router.get`、`@router.post`），最后挂到 `app` 上。把 3.9 节 `main.py` 里的接口整个搬过来，`@app` 换成 `@router`，路径去掉 `/tasks` 前缀：

```python
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import Db
from app.errors import fail, success, task_not_found
from app.models import Task
from app.schemas import TaskCreate, TaskList, TaskOut

# prefix：这个文件里的路径都自动加上 /tasks；tags：/docs 里按这个分组
router = APIRouter(prefix="/tasks", tags=["任务"])


def load_task(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise task_not_found()
    return task


@router.get("")                      # 完整路径 = prefix + "" = /tasks
def list_tasks(session: Db, done: bool | None = None, limit: int = 20) -> dict:
    stmt = select(Task).order_by(Task.id.desc()).limit(limit)
    if done is not None:
        stmt = stmt.where(Task.done == done)
    tasks = session.scalars(stmt).all()
    total = session.scalar(select(func.count()).select_from(Task))
    items = [TaskOut.model_validate(t) for t in tasks]
    return success(TaskList(items=items, total=total or 0))


@router.post("", status_code=201)
def create_task(body: TaskCreate, session: Db) -> dict:
    if session.scalar(select(Task).where(Task.title == body.title, Task.done.is_(False))):
        raise fail(409, "已经有一条同名的未完成任务")
    task = Task(title=body.title, note=body.note)
    session.add(task)
    session.commit()
    return success(TaskOut.model_validate(task), msg="创建成功")


@router.get("/{task_id}")            # 完整路径 = /tasks/{task_id}
def get_task(task_id: int, session: Db) -> dict:
    return success(TaskOut.model_validate(load_task(session, task_id)))


@router.patch("/{task_id}/done")
def finish_task(task_id: int, session: Db) -> dict:
    task = load_task(session, task_id)
    task.done = True
    session.commit()
    return success(TaskOut.model_validate(task))


@router.delete("/{task_id}")
def delete_task(task_id: int, session: Db) -> dict:
    session.delete(load_task(session, task_id))
    session.commit()
    return success(msg="删除成功")
```

```python
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import errors
from app.db import Base, engine
from app.routers import tasks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)   # 启动时建表（第 3.14 节换成 alembic）
    yield


app = FastAPI(title="todo-api", lifespan=lifespan)
errors.install(app)
app.include_router(tasks.router)       # 把路由挂到 app 上
```

```bash
touch app/routers/__init__.py      # 和 3.1 节一样，有它才能 from app.routers import ...
python -m pytest -q                 # 还是 5 passed：只是搬了位置，功能没变
```

- **`prefix="/tasks"`**：这个文件里的路径都自动加上 `/tasks`。`@router.get("")` 就是 `GET /tasks`，`@router.get("/{task_id}")` 就是 `GET /tasks/{task_id}`。
- **`tags=["任务"]`**：`/docs` 里按它分组显示。下一节加上账号接口后，文档里会分成「账号」「任务」两组。
- **`app.include_router(...)`**：挂上才生效，忘了挂，访问就是 404。
- **建表挪到了 `lifespan`**：就是 2.8 节讲的写法，服务启动时执行一次。比写在模块顶层好：测试里导入 `app` 时不会顺手去连真数据库。

以后再加一类业务（比如「标签」），就是新建 `routers/tags.py`，在 `main.py` 里多一行 `include_router`。

## 3.12 注册登录：JWT {#auth}

现在谁都能调接口，所有人看到的也是同一份任务。这一节加上账号：注册、登录，登录后拿到一个 **token**，之后每次请求带上它，后端就知道「你是谁」。下一节再让每个人只看到自己的任务。

```bash
uv pip install pyjwt "pwdlib[argon2]"
```

### 几种登录方式

| | Session + Cookie | JWT（这一节用的） |
|---|---|---|
| 登录后后端记什么 | 在数据库 / Redis 里存一条「会话」，把会话 id 放进 Cookie | 什么都不存，签一个 token 给前端 |
| 之后的请求怎么认人 | 浏览器自动带上 Cookie，后端拿 id 去查会话 | 前端在请求头带 `Authorization: Bearer <token>`，后端验签名 |
| 退出登录 / 踢人下线 | 删掉那条会话，立刻生效 | token 在过期前一直有效，要做黑名单才能提前作废 |
| 适合 | 传统网页、同一个域名 | 前后端分开部署、App、小程序、多个服务之间调用 |

JWT 不用存会话、天然支持跨域，前后端分离的项目用得最多。代价是不好提前作废，所以过期时间不要设太长。

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
    jwt_secret: str = "dev-secret-change-me"  # 签 token 的密钥，线上一定要换成随机长字符串
    token_days: int = 7                       # token 几天后过期
```

生成一个随机密钥写进 `.env`：`python -c "import secrets; print(secrets.token_urlsafe(32))"`。

`app/models.py` 加一张用户表：

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)   # unique：不能重名
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)          # 只存哈希，不存密码
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
```

`app/schemas.py` 加注册登录的请求体和返回格式：

```python
class AuthIn(BaseModel):
    """注册、登录的请求体。"""
    username: str = Field(min_length=2, max_length=20, pattern=r"^\w+$")   # 字母、数字、下划线、汉字
    password: str = Field(min_length=6, max_length=128)


class TokenOut(BaseModel):
    token: str
    username: str
```

密码和 token 的处理单独放一个文件：

```python
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from app.config import settings
from app.db import Db
from app.errors import fail
from app.models import User

# ---------- 密码：只存哈希 ----------
password_hash = PasswordHash.recommended()     # 用 Argon2 算法


def hash_password(password: str) -> str:
    return password_hash.hash(password)        # 每次结果都不一样：里面带了随机的盐


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


# ---------- token：登录后发给前端，之后每次请求带上 ----------
def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),                                            # 这个 token 属于谁
        "exp": datetime.now(UTC) + timedelta(days=settings.token_days),  # 过期时间，过期后 decode 会报错
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


# auto_error=False：没带 token 时不让 FastAPI 自己报 403，交给下面统一返回 401
bearer = HTTPBearer(auto_error=False)


def current_user(
    session: Db,
    cred: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    """依赖：从请求头 Authorization: Bearer <token> 解析出当前用户，不对就 401。"""
    if cred is None:
        raise fail(401, "请先登录")
    try:
        payload = jwt.decode(cred.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise fail(401, "登录已过期，请重新登录") from None
    except jwt.InvalidTokenError:
        raise fail(401, "登录无效，请重新登录") from None
    user = session.get(User, int(payload["sub"]))
    if user is None:                                   # token 是对的，但用户已经被删了
        raise fail(401, "账号不存在，请重新登录")
    return user


CurrentUser = Annotated[User, Depends(current_user)]   # 接口里写 user: CurrentUser 就要求登录
```

```python
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.db import Db
from app.errors import fail, success
from app.models import User
from app.schemas import AuthIn, TokenOut
from app.security import CurrentUser, create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["账号"])


@router.post("/register", status_code=201)
def register(body: AuthIn, session: Db) -> dict:
    if session.scalar(select(User).where(User.username == body.username)):
        raise fail(409, "这个用户名已经被注册了")
    user = User(username=body.username, password_hash=hash_password(body.password))
    session.add(user)
    session.commit()
    # 注册成功直接发 token，等于已经登录，前端不用再调一次登录
    return success(TokenOut(token=create_token(user.id), username=user.username), msg="注册成功")


@router.post("/login")
def login(body: AuthIn, session: Db) -> dict:
    user = session.scalar(select(User).where(User.username == body.username))
    # 用户不存在和密码错误返回同一句话：不告诉别人「这个用户名是存在的」
    if user is None or not verify_password(body.password, user.password_hash):
        raise fail(401, "用户名或密码错误")
    return success(TokenOut(token=create_token(user.id), username=user.username), msg="登录成功")


@router.get("/me")
def me(user: CurrentUser) -> dict:           # 声明要 CurrentUser：没登录进不来
    return success({"id": user.id, "username": user.username})
```

`main.py` 里挂上：`from app.routers import auth, tasks`，再加一行 `app.include_router(auth.router)`。`users` 是一张新表，启动时 `create_all` 会自动建上，不用删库。

- **`current_user` 是一个依赖**：和 3.8 节的 `db_session` 一样，接口参数写 `user: CurrentUser`，FastAPI 就先执行它。没带 token、token 被改过、过期了，都会 `raise fail(401, ...)`，接口函数根本不会执行。它自己也依赖 `Db`，依赖可以一层套一层。
- **`HTTPBearer`**：FastAPI 自带的，负责从请求头 `Authorization: Bearer xxx` 里取出 `xxx`。用它还有个好处：`/docs` 右上角会出现 **Authorize** 按钮，填一次 token，之后点着试的请求都会自动带上。
- **登录失败只说「用户名或密码错误」**：如果分别提示「用户不存在」「密码错误」，别人就能一个个试出哪些用户名注册过。
- **注册成功直接返回 token**：等于注册完就登录了，前端不用再调一次登录接口。
- **`raise ... from None`**：在 `except` 里抛新的错误时，不把原来那个 JWT 的报错串在后面，日志干净一些。

实际运行（curl）：

| 请求 | HTTP | 响应 |
|---|---|---|
| `POST /auth/register` `{"username":"tom","password":"123456"}` | 201 | `{"code":200,"msg":"注册成功","data":{"token":"eyJ...","username":"tom"}}` |
| `GET /auth/me`，带 `Authorization: Bearer eyJ...` | 200 | `{"code":200,"msg":"ok","data":{"id":1,"username":"tom"}}` |
| `GET /auth/me`，不带 token | 401 | `{"code":-1,"msg":"请先登录","data":null}` |
| `POST /auth/login`，密码错 | 401 | `{"code":-1,"msg":"用户名或密码错误","data":null}` |
| `POST /auth/register`，用户名已存在 | 409 | `{"code":-1,"msg":"这个用户名已经被注册了","data":null}` |

**测试**：`client` 这个 fixture 现在两个测试文件都要用，从 `test_tasks.py` 挪到 `tests/conftest.py`。`conftest.py` 是 pytest 约定的文件名，里面的 fixture 同一目录的所有测试文件都能直接用，不用 import。

```python
from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_login_me(client: TestClient) -> None:
    r = client.post("/auth/register", json={"username": "tom", "password": "123456"})
    assert r.status_code == 201
    token = r.json()["data"]["token"]

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.json()["data"]["username"] == "tom"

    r = client.post("/auth/login", json={"username": "tom", "password": "123456"})
    assert r.status_code == 200


def test_wrong_password(client: TestClient) -> None:
    client.post("/auth/register", json={"username": "tom", "password": "123456"})
    r = client.post("/auth/login", json={"username": "tom", "password": "wrong-pass"})
    assert r.status_code == 401
    assert r.json()["msg"] == "用户名或密码错误"


def test_duplicate_username(client: TestClient) -> None:
    client.post("/auth/register", json={"username": "tom", "password": "123456"})
    r = client.post("/auth/register", json={"username": "tom", "password": "654321"})
    assert r.status_code == 409


def test_me_requires_token(client: TestClient) -> None:
    assert client.get("/auth/me").json()["msg"] == "请先登录"
    r = client.get("/auth/me", headers={"Authorization": "Bearer abc"})
    assert r.status_code == 401
    assert r.json()["msg"] == "登录无效，请重新登录"
```

## 3.13 一对多和分页 {#relations-paging}

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
    ...
    # 一对多：一个用户有多条任务。不是表里的列，是 Python 里方便取关联数据用的
    tasks: Mapped[list[Task]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    ...
    # 外键：这条任务属于哪个用户，值是 users 表的 id；index=True 加索引，按用户查更快
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
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
session.add(tom)
session.commit()

print([t.title for t in tom.tasks])       # ['写笔记', '读书']
print(session.get(Task, 1).user.username) # tom
session.delete(tom)                       # 删 tom，他的两条任务也跟着删了（cascade）
```

`relationship` 适合「拿一个对象顺带看看关联的东西」。要按条件筛选、分页、计数，还是自己写 `select(...).where(...)`，下面的接口就是这样做的。

> **多对多**（比如任务和标签：一个任务多个标签，一个标签多个任务）要再建一张中间表，只存 `task_id` 和 `tag_id` 两列。原理一样，用到再查文档。

### 接口：加上「是不是自己的」

`schemas.py` 里 `TaskList` 加两个字段，告诉前端现在是第几页：

```python
class TaskList(BaseModel):
    items: list[TaskOut]      # 模型可以嵌套
    total: int                # 符合条件的一共多少条（不是这一页的条数）
    page: int
    size: int
```

```python
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import Db
from app.errors import fail, success, task_not_found
from app.models import Task, User
from app.schemas import TaskCreate, TaskList, TaskOut
from app.security import CurrentUser

router = APIRouter(prefix="/tasks", tags=["任务"])


def load_task(session: Session, task_id: int, user: User) -> Task:
    """取自己的一条任务。别人的任务也当成不存在：返回 404，不告诉对方「有这条，但不是你的」。"""
    task = session.get(Task, task_id)
    if task is None or task.user_id != user.id:
        raise task_not_found()
    return task


@router.get("")
def list_tasks(
    user: CurrentUser,
    session: Db,
    done: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,              # 第几页，从 1 开始
    size: Annotated[int, Query(ge=1, le=100)] = 20,     # 每页几条，最多 100，防止一次拉太多
) -> dict:
    conditions = [Task.user_id == user.id]               # 只查自己的
    if done is not None:
        conditions.append(Task.done == done)

    total = session.scalar(select(func.count()).select_from(Task).where(*conditions))   # 总数和列表用同一组条件
    stmt = (
        select(Task)
        .where(*conditions)
        .order_by(Task.id.desc())
        .offset((page - 1) * size)                       # 跳过前面几页
        .limit(size)
    )
    items = [TaskOut.model_validate(t) for t in session.scalars(stmt)]
    return success(TaskList(items=items, total=total or 0, page=page, size=size))


@router.post("", status_code=201)
def create_task(body: TaskCreate, user: CurrentUser, session: Db) -> dict:
    same = select(Task).where(Task.user_id == user.id, Task.title == body.title, Task.done.is_(False))
    if session.scalar(same):
        raise fail(409, "已经有一条同名的未完成任务")
    task = Task(user_id=user.id, title=body.title, note=body.note)
    session.add(task)
    session.commit()
    return success(TaskOut.model_validate(task), msg="创建成功")


@router.get("/{task_id}")
def get_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    return success(TaskOut.model_validate(load_task(session, task_id, user)))


@router.patch("/{task_id}/done")
def finish_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    task = load_task(session, task_id, user)
    task.done = True
    session.commit()
    return success(TaskOut.model_validate(task))


@router.delete("/{task_id}")
def delete_task(task_id: int, user: CurrentUser, session: Db) -> dict:
    session.delete(load_task(session, task_id, user))
    session.commit()
    return success(msg="删除成功")
```

- **每个接口都加了 `user: CurrentUser`**：不登录访问任何任务接口都是 401。
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
- **`total` 和列表用同一组条件**：前端靠 `total` 算总页数。3.9 节的 `total` 数的是整张表，没带 `done` 筛选，其实是个 bug；现在两条查询共用 `conditions`，不会再对不上。
- **一定要 `order_by`**：不排序的话，数据库不保证每次返回的顺序一样，翻页时可能有的数据重复出现、有的永远看不到。

> 页数很深（比如第 10000 页）时，`OFFSET` 会越来越慢，因为数据库要先数过前面所有行。那种场景用「游标分页」：前端传上一页最后一条的 id，后端查 `where id < 那个 id`。一般的后台列表用 `page / size` 就够了。

表结构又变了，**再删一次 `todo.db`**。这种「改一次表就删一次库」的做法到这里为止，下一节换成 alembic。

**测试**：`conftest.py` 里加一个注册用户、返回请求头的小工具，任务的测试都带上它：

```python
# tests/conftest.py（末尾加上）
def login(client: TestClient, username: str = "tom") -> dict:
    """注册一个用户，返回带 token 的请求头。"""
    r = client.post("/auth/register", json={"username": username, "password": "123456"})
    return {"Authorization": f"Bearer {r.json()['data']['token']}"}


@pytest.fixture
def auth(client: TestClient) -> dict:
    return login(client)
```

原来的测试都改成带上 `headers=auth`（比如 `client.post("/tasks", json={...}, headers=auth)`），再加三个新的：

```python
def test_requires_login(client: TestClient) -> None:
    r = client.get("/tasks")
    assert r.status_code == 401


def test_users_cannot_see_each_other(client: TestClient) -> None:
    tom, jerry = login(client, "tom"), login(client, "jerry")
    task_id = client.post("/tasks", json={"title": "tom 的任务"}, headers=tom).json()["data"]["id"]

    assert client.get("/tasks", headers=jerry).json()["data"]["total"] == 0      # 列表里看不到
    assert client.get(f"/tasks/{task_id}", headers=jerry).status_code == 404     # 直接猜 id 也拿不到
    assert client.delete(f"/tasks/{task_id}", headers=jerry).status_code == 404  # 删不掉
    assert client.get(f"/tasks/{task_id}", headers=tom).status_code == 200       # 自己还在


def test_pagination(client: TestClient, auth: dict) -> None:
    for i in range(1, 26):                                   # 建 25 条
        client.post("/tasks", json={"title": f"任务{i}"}, headers=auth)
    data = client.get("/tasks", params={"page": 2, "size": 10}, headers=auth).json()["data"]
    assert data["total"] == 25
    assert [t["title"] for t in data["items"]][:2] == ["任务15", "任务14"]   # 倒序，第 2 页从第 11 条开始
    assert len(client.get("/tasks", params={"page": 3, "size": 10}, headers=auth).json()["data"]["items"]) == 5
    assert client.get("/tasks", params={"size": 500}, headers=auth).status_code == 422
```

`test_tasks.py` 开头要 `from tests.conftest import login`：fixture 能自动用，普通函数还是要 import。跑一下应该是 `12 passed`。

## 3.14 数据库迁移：Alembic {#alembic}

前面每次改表都要删库重建，因为 `create_all` 只会建不存在的表，不会改已有的表。本地数据删了无所谓，**线上的数据是不能删的**。迁移工具解决的就是「表结构要改，数据要留着」：

- 每次改表，生成一个**迁移脚本**，写着「这次加了哪一列」「建了哪张表」。
- 数据库里多一张 `alembic_version` 表，记着当前执行到哪个版本。
- `alembic upgrade head` 把还没执行的脚本按顺序执行一遍。本地、同事电脑、线上，都用同一套脚本升到同一个结构。

迁移脚本要提交到 git，和代码一起走。

```bash
uv pip install alembic
alembic init migrations        # 在 todo-api/ 下生成 alembic.ini 和 migrations/ 目录
```

### 配置：改 `migrations/env.py` 的两处

生成的 `env.py` 不知道你的数据库在哪、表长什么样。找到 `target_metadata = None` 那一段，换成：

```python
# ---- 改动 ①：数据库地址和项目用同一份配置，不在 alembic.ini 里再写一遍 ----
from app import models  # noqa: E402,F401  导入一下，表才会登记到 Base.metadata 上
from app.config import settings  # noqa: E402
from app.db import Base  # noqa: E402

config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))  # % 要写成 %%

# ---- 改动 ②：告诉 alembic「代码里的表长什么样」，autogenerate 拿它和数据库对比 ----
target_metadata = Base.metadata
```

再在文件里两处 `context.configure(...)` 的参数里各加一行 `render_as_batch=True`：SQLite 不支持删列、改列，开了这个，alembic 会用「建新表 → 复制数据 → 删旧表」的方式绕过去。用 Postgres 的话加了也没影响。

`.replace("%", "%%")`：`alembic.ini` 的格式把 `%` 当特殊字符，数据库密码里有 `%` 时不转义会报错。

最后，`main.py` 里的 `lifespan` 和 `create_all` **删掉**：表结构从此只由 alembic 管。

```python
app = FastAPI(title="todo-api")         # 不再 create_all：表结构交给 alembic
```

测试里的 `create_all` 留着：测试用的是内存库，每次都是全新的，直接建表最省事。

### 第一次：从现在的表结构生成迁移

```bash
rm -f todo.db                                         # 最后一次删库：之后都靠迁移
alembic revision --autogenerate -m "create users and tasks"
alembic upgrade head
```

`--autogenerate` 会把代码里的表和数据库里的表做对比，把差别写成脚本，放在 `migrations/versions/` 下面：

```python
"""create users and tasks

Revision ID: 8b3af2c15abf
Revises:
"""
revision: str = '8b3af2c15abf'
down_revision: Union[str, Sequence[str], None] = None    # 上一个版本：第一个没有


def upgrade() -> None:                                    # 升级：执行这个
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    ...
    )
    op.create_table('tasks', ...)
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tasks_user_id'), ['user_id'], unique=False)


def downgrade() -> None:                                  # 回退：执行这个，把 upgrade 做的撤销掉
    ...
    op.drop_table('tasks')
    op.drop_table('users')
```

执行完，数据库里多了 `alembic_version` 表，记着当前版本 `8b3af2c15abf`。

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
sqlite3.OperationalError: Cannot add a NOT NULL column with default value NULL
```

原因：`default=0` 是 **Python 这边**的默认值，只在 SQLAlchemy 插入新数据时生效，数据库根本不知道。表里已经有的那几行，新加的 `priority` 列填什么？数据库只能填 NULL，而这一列又规定了不能为 NULL。

改成同时写 `server_default`：这是**数据库这边**的默认值，加列时已有的行会自动填上它。删掉刚才生成的那个迁移文件，重新生成：

```python
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
```

```bash
rm migrations/versions/*_add_task_priority.py
alembic revision --autogenerate -m "add task priority"
alembic upgrade head            # Running upgrade 8b3af2c15abf -> 23a1f64ac3fa, add task priority
```

生成的脚本：

```python
def upgrade() -> None:
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_column('priority')
```

原来的数据都还在，`priority` 自动是 0。要在接口里返回，`TaskOut` 也加上 `priority: int`。

**给已经有数据的表加「不能为空」的列，一定要给 `server_default`。** 这个坑本地发现不了（本地经常是空表），一上线就炸。

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
8b3af2c15abf -> 23a1f64ac3fa (head), add task priority
<base> -> 8b3af2c15abf, create users and tasks
```

- **生成的脚本一定要打开看一眼再 upgrade**。autogenerate 不是万能的：比如把列**改名**，它会识别成「删掉旧列 + 加一列新的」，数据就丢了。这种要手动把脚本改成 `batch_op.alter_column('旧名', new_column_name='新名')`。
- **已经执行过、提交过的迁移脚本不要再改**。要改就再生成一个新的。

### 换成 PostgreSQL

模型和迁移脚本都不用改，只换连接地址：

```bash
uv pip install "psycopg[binary]"         # Postgres 的驱动
```

```
# .env
DATABASE_URL=postgresql+psycopg://用户名:密码@localhost:5432/todo
```

```bash
alembic upgrade head                     # 在新库上从头建一遍
uvicorn app.main:app --reload
```

- 地址开头是 `postgresql+psycopg://`：`+psycopg` 指定用哪个驱动。云数据库（比如 Neon）给的地址一般是 `postgresql://...`，要手动加上 `+psycopg`，否则 SQLAlchemy 会去找另一个没装的驱动。
- 本地装 Postgres：Mac 上 `brew install postgresql@17`，或者直接用 Neon 这类云数据库的免费版，下一节部署也会用到。
- 这一节的代码在 Postgres 上实际跑过：两个迁移都能执行，接口正常。有一点不同：返回的时间会带上数据库所在的时区，比如 `2026-11-12T19:58:42+08:00`，和 SQLite 返回的 `2026-11-12T11:58:42Z` 是同一个时刻，前端用 `new Date(...)` 解析结果一样。

## 3.15 上线：CORS、中间件、部署 {#deploy}

最后三件事：让浏览器里的前端能调到接口，给每个请求记日志，部署到线上。

### CORS：跨域

前端在 `http://localhost:5173`，后端在 `http://localhost:8000`，端口不同就算**不同的源**。浏览器出于安全，默认不让网页读别的源返回的数据。这时候浏览器会先问后端一句（发一个 `OPTIONS` 请求，叫**预检**）：「`localhost:5173` 的页面能调你吗？」后端回答可以，浏览器才把真正的请求发出去。

所以 CORS 是**后端**的配置，前端改不了。FastAPI 用自带的中间件：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],                 # 所有请求方法
    allow_headers=["*"],                 # 所有请求头，包括 Authorization
)
```

`app/config.py` 加一个配置，线上把前端的正式网址写进去：

```python
    # 允许哪些前端网址跨域调用；环境变量里写成 JSON：CORS_ORIGINS='["https://todo.example.com"]'
    cors_origins: list[str] = ["http://localhost:5173"]
```

- **`allow_origins` 写具体网址，不要图省事写 `["*"]`**。本笔记站的后端写的是 `*`，因为它的 token 在请求头里、不用 Cookie，任何网页都拿不到别人的 token，开放也没风险。用 Cookie 登录的项目绝不能写 `*`（这种情况浏览器也不允许）。
- 用 curl、Postman 调接口不会遇到跨域：CORS 只是浏览器的限制。所以「Postman 能通、浏览器报 CORS」就是这个问题。

### 中间件：每个请求都经过的地方

**中间件**包在所有接口外面：请求进来先经过它，再到接口；接口的响应出去，也要再经过它。适合放「每个请求都要做」的事：记日志、统计耗时、加响应头。上面的 CORS 也是一个中间件。

```python
import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("todo-api")


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start = time.perf_counter()
    response = await call_next(request)          # 交给后面的路由去处理，拿到响应
    ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s → %s %.0fms", request.method, request.url.path, response.status_code, ms)
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"   # 也可以改响应：加个响应头
    return response
```

```
2026-11-12 19:59:24,565 INFO GET / → 200 7ms
2026-11-12 19:59:24,574 INFO GET /tasks → 401 1ms
```

`call_next(request)` 之前的代码在接口执行**前**跑，之后的在接口执行**后**跑，和 2.8 节 `yield` 前后是一个意思。日志用 2.3 节的 `logging`，不用 `print`：线上能按级别过滤，也能统一收集。

完整的 `main.py`：

```python
from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app import errors
from app.config import settings
from app.routers import auth, tasks

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("todo-api")

app = FastAPI(title="todo-api")         # 不再 create_all：表结构交给 alembic
errors.install(app)

# 跨域：允许这些网址的前端页面调接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],                 # 所有请求方法
    allow_headers=["*"],                 # 所有请求头，包括 Authorization
)


# 中间件：每个请求进来、出去都会经过这里
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start = time.perf_counter()
    response = await call_next(request)          # 交给后面的路由去处理，拿到响应
    ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s → %s %.0fms", request.method, request.url.path, response.status_code, ms)
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"   # 也可以改响应：加个响应头
    return response


app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["健康检查"])
def health() -> dict:
    """部署后先访问这个，确认服务起来了。"""
    return errors.success({"status": "ok"})
```

加一个 `/` 接口当**健康检查**：部署完先访问它，返回 `ok` 说明服务起来了；也可以交给监控定时访问。

### 部署到 Vercel

本笔记站的后端（仓库里的 `backend/` 目录）就是这么部署的，可以对照着看。

**1. 线上数据库**：Vercel 上的函数用完就销毁，磁盘也是临时的，SQLite 文件存不住，只能用云数据库。在 Vercel 项目的 Storage 里一键建一个 Neon（Postgres，有免费额度），它会自动设好 `DATABASE_URL` 环境变量。记得按上一节说的把开头改成 `postgresql+psycopg://`。

**2. 入口文件和依赖**：项目根目录加一个 `index.py`，Vercel 找到里面的 `app` 就能运行：

```python
# Vercel 的入口：找到这个文件里的 app 就能跑
from app.main import app  # noqa: F401
```

依赖写进 `pyproject.toml`（2.2 节）或 `requirements.txt`，Vercel 会自动安装。`uvicorn`、`pytest` 这类只在本地用的不用写进去。

**3. 连接池和密钥**：`app/config.py` 加一个 `vercel` 配置，和一个检查：

```python
    vercel: bool = False                      # Vercel 上会自动设置 VERCEL=1

    @model_validator(mode="after")
    def check_secret(self) -> Settings:
        # 线上还在用开发密钥，等于谁都能伪造 token：直接启动失败，比悄悄上线好
        if self.vercel and self.jwt_secret == DEV_SECRET:
            raise ValueError("线上必须设置 JWT_SECRET 环境变量")
        return self
```

`app/db.py` 里，在 Vercel 上不用连接池：

```python
from sqlalchemy.pool import NullPool

engine = create_engine(
    settings.database_url,
    echo=settings.debug,                                 # debug 时打印每条 SQL
    # Vercel 上每个请求可能是一个新的函数实例，自己维护连接池没意义还占连接：用完就关
    poolclass=NullPool if settings.vercel else None,     # None = 用默认的连接池
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

**测试**：加两个，确认健康检查和 CORS 生效（应该是 `14 passed`）：

```python
from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/")
    assert r.json()["data"] == {"status": "ok"}
    assert r.headers["X-Response-Time"].endswith("ms")


def test_cors_preflight(client: TestClient) -> None:
    # 浏览器跨域发带 Authorization 的请求前，会先发一个 OPTIONS「预检」
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    }
    r = client.options("/tasks", headers=headers)
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"

    r = client.options("/tasks", headers={**headers, "Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in r.headers      # 不在名单里的网址拿不到许可
```

### 阶段三做完了什么

从 3.1 的一个 hello 接口，到现在是一个能上线的多用户后端：

| 能力 | 在哪一节 |
|---|---|
| 接口、参数、请求体校验 | 3.2、3.3 |
| 统一的响应格式和错误处理 | 3.4 |
| 手写 SQL、Postgres 和 MySQL 的区别 | 3.5 |
| 数据库增删改查、依赖注入 | 3.6～3.9 |
| 自动化测试 | 3.10 |
| 按业务拆文件、配置管理 | 3.11 |
| 注册登录、密码哈希、JWT | 3.12 |
| 数据隔离、一对多、分页 | 3.13 |
| 数据库迁移、换 Postgres | 3.14 |
| 跨域、请求日志、部署 | 3.15 |

接下来的阶段四，就是在这样的后端里接入大模型。
