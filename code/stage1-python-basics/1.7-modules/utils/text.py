# 笔记里只写了「里面有 def shout(s): ...」，这里补一个最简单的实现，方便 main.py 能导入运行
def shout(s: str) -> str:
    return s.upper() + "!"
