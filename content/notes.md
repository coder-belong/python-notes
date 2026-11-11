# Python 入门笔记

从基础语法一路学到用 FastAPI 写接口、连数据库、写测试。

- **阶段一：Python 语言基础**（第 1–12 节）：只讲常用的写法，不常用的先跳过。
- **阶段二：Python 进阶与工程化**（第 13–15 节）：类型注解、日志和配置、异步。
- **阶段三：Python 后端开发**（第 16–24 节）：用 FastAPI + SQLAlchemy 从零做一个 todo 接口项目。

每节的代码都建议自己敲一遍、跑一遍。代码在 Python 3.12 上跑通过，注释里写的是实际输出。

---

## 0. 准备环境 {#setup}

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

## 1. 变量、类型、缩进 {#variables}

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
- 标注只是提示，Python 运行时不会检查。更多写法集中在第 13 节。

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

## 2. 判断和循环 {#control-flow}

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

## 3. 列表、字典、元组、集合 {#collections}

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
users = [{"name": n, "age": a} for n, a in zip(names, ages)]
print(users)                             # [{'name': 'Tom', 'age': 18}, {'name': 'Jerry', 'age': 20}]

# 再带上从 1 开始的序号；(n, a) 要加括号，因为 zip 给出的每一项是一对值
users = [{"id": i, "name": n, "age": a} for i, (n, a) in enumerate(zip(names, ages), start=1)]
print(users[1])                          # {'id': 2, 'name': 'Jerry', 'age': 20}
```

要组装成对象，见第 10 节的 dataclass：`[User(n, a) for n, a in zip(names, ages)]`。

## 4. 推导式：一行生成列表 / 字典 {#comprehensions}

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

## 5. 函数 {#functions}

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

## 6. 迭代器、生成器、装饰器 {#iter-gen-deco}

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

Path("a.txt").write_text("第一行\n第二行\n", encoding="utf-8")   # 先准备一个小文件（文件读写见第 12 节）

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

第 22 节的数据库会话、第 24 节的 pytest fixture 都用 `yield` 写「先准备 → 交出去用 → 用完收尾」，原理就是这里的「暂停再继续」。

### 装饰器：给函数包一层

函数本身也是一个值，可以当参数传。装饰器就是「接收一个函数，返回包了一层的新函数」，用来给函数加功能而不改它的代码。

```python
import time

def timer(func):                     # 接收原函数
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

**带参数的装饰器**：`@app.get("/tasks")` 多了一对括号，意思是先调用 `app.get("/tasks")`，它返回一个装饰器，再用这个装饰器去包下面的函数。等价于：

```python
# @app.get("/tasks")
# def list_tasks(): ...
#
# 等于：
# list_tasks = app.get("/tasks")(list_tasks)
```

## 7. 模块和导入 {#modules}

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

## 8. 类：属性和方法 {#classes}

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

继承、多态见第 9 节。

## 9. 继承和多态 {#inheritance}

**继承**：子类自动拥有父类的属性和方法，可以覆盖（重写），也可以加新的。

```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."


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


animals: list[Animal] = [Dog("旺财", "柴犬"), Cat("咪咪"), Animal("某某")]
for a in animals:
    print(a.speak())
# 旺财: 汪
# 咪咪: 喵
# ...
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
- 最常见的继承是框架要求的：`class BalanceError(Exception)`（第 11 节）、`class TaskCreate(BaseModel)`（pydantic，第 18 节）、`class Task(Base)`（SQLAlchemy，第 20 节）。

## 10. dataclass：只存数据的类 {#dataclass}

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
| 接口收到的请求、返回的响应（要校验） | pydantic 的 `BaseModel`（第 18 节） |
| 有复杂逻辑的类、异常类 | 普通 class，自己写 `__init__` |

## 11. 异常 {#exceptions}

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
print(to_int("abc"))    # 转换失败： invalid literal for int() with base 10: 'abc' / ... / None
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

**主动抛错 `raise`**：执行到 `raise`，当前函数立刻停下，后面的代码都不执行（和 `return` 一样）。区别是停下之后去哪里：

- `return`：把结果交回给调用的地方，程序照常往下走。
- `raise`：错误一层层往外抛，找有没有 `try/except` 接住；接住了就跳到 `except` 里继续执行，没人接就整个程序终止并打印报错。`finally` 里的代码不管怎样都会执行。

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

## 12. 文件和 JSON {#files-json}

```python
import json
from pathlib import Path

folder = Path("data")
folder.mkdir(exist_ok=True)                # 建文件夹，已存在不报错
f = folder / "user.json"                   # 用 / 拼路径

data = {"name": "Tom", "tags": ["a", "b"]}
f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")   # 写
loaded = json.loads(f.read_text(encoding="utf-8"))                                # 读
print(loaded["tags"])                      # ['a', 'b']

print(f.exists(), f.name, f.suffix)        # True user.json .json
for p in folder.glob("*.json"):            # 找文件
    print(p)
```

- `json.dumps` / `json.loads`：对象 ↔ **字符串**（带 s = string）。
- `json.dump` / `json.load`：对象 ↔ **文件对象**。
- `ensure_ascii=False`：中文原样写出，不变成 `中`。
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

把前面散在各节的类型注解集中讲清楚，再加上写项目离不开的日志、配置和异步。

## 13. 类型注解：给变量和函数标类型 {#type-hints}

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
- 想在**运行时**真的校验数据（比如接口收到的 JSON）：用 pydantic（第 18 节），它按注解检查、转换类型，不对就报错。

**写到什么程度**：函数的参数和返回值都写；变量一眼能看出类型的就不写；一时写不出来的类型先用 `Any`（`from typing import Any`），别卡在类型上。

## 14. 日志、环境变量、时间 {#logging-env-time}

```python
import logging
import os
from datetime import UTC, datetime, timedelta

logging.basicConfig(level=logging.INFO)     # 程序入口配置一次：INFO 及以上都输出
log = logging.getLogger(__name__)           # 每个文件一个 logger，名字是模块名

log.info("开始处理 %s 条", 3)                # 用 %s 占位，不要自己拼字符串
log.warning("快满了")
log.error("失败了")

# 环境变量：密码、地址这类配置不写死在代码里
db_url = os.environ.get("DATABASE_URL", "sqlite:///todo.db")   # 没配就用默认值
print(db_url)

# 时间
now = datetime.now(UTC)                     # 带时区的当前时间，存库和返回接口都用 UTC
print(now.isoformat())                      # 2026-11-10T07:00:00.123456+00:00
print(now.strftime("%Y-%m-%d %H:%M:%S"))    # 2026-11-10 07:00:00
print(now - timedelta(days=3))              # 3 天前
```

**为什么用 logging 不用 print**：能分级别（线上只看 warning 以上）、自动带时间和模块名、可以统一输出到文件或日志系统。

| 级别 | 用在哪 |
|---|---|
| `debug` | 调试细节，平时不输出 |
| `info` | 正常的关键步骤 |
| `warning` | 不正常但还能继续 |
| `error` | 出错了 |

## 15. async / await {#async}

`async def` 定义的是**协程函数**：遇到要等待的操作（网络请求、sleep）时，可以先让出去执行别的任务，等好了再回来。

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

**为什么写 `asyncio.run(main())`，不直接 `main()`**

调用 `async def` 定义的函数时，函数体**不会执行**，只会得到一个「协程对象」：

```python
async def hello():
    print("运行了")

coro = hello()
print(coro)          # <coroutine object hello at 0x...>   "运行了" 没打印
coro.close()         # 不 close 的话会警告：coroutine 'hello' was never awaited
```

协程要靠**事件循环**来驱动：它记着每个任务在等什么，谁等好了就让谁从 `await` 的地方接着跑。`asyncio.run(main())` 做三件事：

1. 创建一个事件循环；
2. 运行 `main()` 直到结束，返回 `main` 的返回值；
3. 关闭事件循环。

`await` 只能写在 `async def` 里，而程序最外层是普通代码，所以需要 `asyncio.run` 作为入口，从普通代码进入 async 的世界：

```
普通代码 ──asyncio.run()──→ main() ──await──→ fetch() ──await──→ asyncio.sleep()
```

- 整个程序只在最外层调用一次 `asyncio.run(main())`；在 async 函数里面要用 `await`，不能再调用 `asyncio.run`（会报错，因为事件循环已经在跑了）。
- 用 FastAPI 不需要写 `asyncio.run`：uvicorn 启动时已经建好了事件循环，你写的 `async def` 接口由它来调用。

- `await` 只能写在 `async def` 里面。
- 在 async 函数里**不要用 `time.sleep()`**，它会卡住整个程序；要用 `await asyncio.sleep()`。
- 写 FastAPI 接口时，普通的 `def` 就够用（FastAPI 会放到线程池里跑），入门阶段不必纠结。

---

# 阶段三：Python 后端开发

做一个 todo 接口项目：用 FastAPI 写接口，SQLAlchemy 把数据存进 SQLite，pytest 写测试。

## 16. 项目准备 {#project-setup}

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
| python-dotenv | 启动时读取 `.env` 文件里的配置（第 20 节） |

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

## 17. 第一个接口 {#first-api}

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

## 18. pydantic：请求体和响应格式 {#pydantic}

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
    model_config = ConfigDict(from_attributes=True)   # 允许直接从对象的属性读值（第 23 节用）

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

**`from_attributes=True`**：`TaskOut` 加了这个配置后，可以用 `TaskOut.model_validate(对象)` 直接从一个对象上按字段名读取同名属性来创建，不用一个个字段手写 `TaskOut(id=task.id, title=task.title, ...)`。第 23 节就用它把数据库里的 `Task` 转成返回给前端的 `TaskOut`。

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

## 19. 统一响应格式和错误处理 {#errors}

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
- **为什么失败用 `raise` 而不是 `return`**：`raise` 会让函数立刻停下，而且不管嵌套几层都能直接抛到 FastAPI。比如第 23 节的 `load_task()` 是被接口调用的普通函数，它在里面 `raise task_not_found()`，接口不用再判断一次返回值。
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

参数校验失败用 422 还是 400，团队统一就行，很多项目用 400。如果改成 400，第 24 节测试里 `test_empty_title_rejected` 的 422 也要跟着改。

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

## 20. SQLAlchemy：连数据库、用类定义表 {#sqlalchemy}

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
- **表结构改了要删库重建**：`create_all` 只会建不存在的表，不会给已有的表加列。已经跑过旧版本的话，先删掉 `todo.db` 再启动，否则会报 `no such column: tasks.updated_at`。正式项目用 alembic 处理这种改动。

## 21. Session：在接口里增删改查 {#session}

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

**发现问题了吗**：每个接口都在重复 `with SessionLocal() as session:`、查不到就 `raise fail(404, ...)`。下一节用依赖注入把「开会话」交给 FastAPI，第 23 节再把「查不到就 404」抽成 `load_task()`。

## 22. 依赖注入：接口里拿到数据库会话 {#dependency-injection}

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

## 23. 完整的 todo 接口 {#todo-api}

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
Base.metadata.create_all(engine)   # 练习用：启动时自动建表；正式项目用 alembic 管理表结构


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

- **`TaskOut.model_validate(task)`**：把数据库里的 `Task` 对象转成返回给前端的 `TaskOut`（第 18 节加了 `from_attributes=True` 才能这样用）。
- **为什么不能直接 `success(task)`**：`Task` 是 SQLAlchemy 的数据库对象，FastAPI 不知道怎么把它转成 JSON，会报错返回 500。转成 `TaskOut` 还有一个好处：只输出 `TaskOut` 里定义的字段，以后表里加了不该给前端看的列，也不会被带出去。

启动：`uvicorn app.main:app --reload`，到 `/docs` 里点着试，或者用 curl：

```bash
curl -X POST http://127.0.0.1:8000/tasks -H 'Content-Type: application/json' -d '{"title": "写笔记"}'
curl http://127.0.0.1:8000/tasks
curl -X PATCH http://127.0.0.1:8000/tasks/1/done
curl -i http://127.0.0.1:8000/tasks/99      # -i 显示状态码：404 + {"code": -1, "msg": "没有这个任务", "data": null}
```

## 24. pytest：给接口写测试 {#pytest}

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
