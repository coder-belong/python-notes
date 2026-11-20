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
