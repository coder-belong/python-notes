# main.py
import json                       # 导入整个模块，用的时候写 json.dumps(...)
from pathlib import Path          # 只导入需要的名字
from utils.text import shout      # 从自己的包里导入：包名.文件名
from datetime import datetime as dt   # 起别名


# ---- 只在直接运行时执行的代码 ----
def main() -> None:
    print("运行了")

if __name__ == "__main__":   # 被别的文件 import 时不执行
    main()
