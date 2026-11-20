# 先运行 demo.py 生成 data/user.json，再运行这个文件
with open("data/user.json", encoding="utf-8") as fp:   # with 结束时自动关文件
    for line in fp:
        print(line.rstrip())
