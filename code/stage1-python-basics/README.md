# 阶段一：Python 语言基础（示例代码）

代码来自 `python-notes/content/notes.md` 的「阶段一」，每节一个目录。

## 建环境

```bash
cd code/stage1-python-basics
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python pydantic     # 只有 1.8 的 to_dict.py 用到
```

**运行方式**：先 `cd` 进对应小节目录，再用 `../.venv/bin/python 文件名` 运行（示例里的相对路径、`import` 都以当前目录为准）。也可以先 `source .venv/bin/activate`，之后直接 `python 文件名`。

## 文件一览

| 小节 | 文件 | 说明 | 运行命令 |
|---|---|---|---|
| 1.1 变量、类型、缩进 | `1.1-variables/01_basic.py` | 变量类型、类型标注、缩进、字符串方法、split/join、切片、数字运算（本节所有代码块合成一个文件） | `cd 1.1-variables && ../.venv/bin/python 01_basic.py` |
| 1.2 判断和循环 | `1.2-control-flow/control_flow.py` | if/elif/else、三元表达式、and/not/is None、真假值、for/while/break/continue | `cd 1.2-control-flow && ../.venv/bin/python control_flow.py` |
| 1.3 列表、字典、元组、集合 | `1.3-collections/containers.py` | list/dict/tuple/set 基本操作、拆包、enumerate、zip | `cd 1.3-collections && ../.venv/bin/python containers.py` |
| | `1.3-collections/unpack_error.py` | **故意报错**：拆包个数对不上，第一行就抛 `ValueError` | `cd 1.3-collections && ../.venv/bin/python unpack_error.py` |
| | `1.3-collections/build_users.py` | 两个列表组装成字典 / 字典列表 | `cd 1.3-collections && ../.venv/bin/python build_users.py` |
| 1.4 推导式 | `1.4-comprehensions/comprehensions.py` | 列表/字典推导式和等价的 for 写法 | `cd 1.4-comprehensions && ../.venv/bin/python comprehensions.py` |
| 1.5 函数 | `1.5-functions/functions.py` | 默认参数、多返回值、`*` 强制关键字、`*args/**kwargs`、lambda + sorted/max | `cd 1.5-functions && ../.venv/bin/python functions.py` |
| 1.6 迭代器、生成器、装饰器 | `1.6-iter-gen-deco/iterators.py` | iter/next、迭代器只能走一遍、自写 `Countdown` 迭代器类 | `cd 1.6-iter-gen-deco && ../.venv/bin/python iterators.py` |
| | `1.6-iter-gen-deco/generators.py` | yield 生成器、生成器表达式（运行时会写出 `a.txt`） | `cd 1.6-iter-gen-deco && ../.venv/bin/python generators.py` |
| | `1.6-iter-gen-deco/decorators.py` | `@timer` 装饰器、`@wraps` | `cd 1.6-iter-gen-deco && ../.venv/bin/python decorators.py` |
| 1.7 模块和导入 | `1.7-modules/main.py` + `utils/__init__.py` + `utils/text.py` | 包和导入、`if __name__ == "__main__"` | `cd 1.7-modules && ../.venv/bin/python main.py` |
| 1.8 类 | `1.8-classes/counter.py` | 类、`__init__`、方法、`__repr__` | `cd 1.8-classes && ../.venv/bin/python counter.py` |
| | `1.8-classes/object_vs_dict.py` | **故意报错**：对象用方括号取值抛 `TypeError` | `cd 1.8-classes && ../.venv/bin/python object_vs_dict.py` |
| | `1.8-classes/to_dict.py` | dataclass 的 `asdict`、pydantic 的 `model_dump`（需要 pydantic） | `cd 1.8-classes && ../.venv/bin/python to_dict.py` |
| | `1.8-classes/classmethod_demo.py` | `@classmethod` 另一种创建对象的方式 | `cd 1.8-classes && ../.venv/bin/python classmethod_demo.py` |
| 1.9 继承和多态 | `1.9-inheritance/inheritance.py` | 继承、super、多态、isinstance、抽象基类、鸭子类型 | `cd 1.9-inheritance && ../.venv/bin/python inheritance.py` |
| 1.10 dataclass | `1.10-dataclass/task_dataclass.py` | `@dataclass`、`field(default_factory=list)` | `cd 1.10-dataclass && ../.venv/bin/python task_dataclass.py` |
| 1.11 异常 | `1.11-exceptions/exceptions.py` | try/except/else/finally、多个 except、raise、自定义异常 | `cd 1.11-exceptions && ../.venv/bin/python exceptions.py` |
| 1.12 文件和 JSON | `1.12-files-json/demo.py` | Path 建文件夹、写读 JSON、文件信息、glob（运行时会生成 `data/`） | `cd 1.12-files-json && ../.venv/bin/python demo.py` |
| | `1.12-files-json/read_by_line.py` | 按行读文件，**先运行 demo.py** 生成 `data/user.json` | `cd 1.12-files-json && ../.venv/bin/python read_by_line.py` |
| | `1.12-files-json/with_demo.py` | `with` 和等价的 try/finally 写法（会写出 `a.txt`，无输出） | `cd 1.12-files-json && ../.venv/bin/python with_demo.py` |

运行后生成的 `a.txt`、`data/` 都是示例产物，可以随时删掉。
