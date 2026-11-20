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


# ---- 用生成器改写 Countdown ----
def countdown(start: int):
    for n in range(start, 0, -1):
        yield n


print(list(countdown(3)))     # [3, 2, 1]

# ---- 生成器表达式 ----
squares = [n * n for n in range(5)]     # 列表：5 个结果全部算好放在内存里
print(squares)                          # [0, 1, 4, 9, 16]

total = sum(n * n for n in range(1_000_000))   # 生成器：边算边加，不建一百万个元素的列表
print(total)                                   # 333332833333500000
