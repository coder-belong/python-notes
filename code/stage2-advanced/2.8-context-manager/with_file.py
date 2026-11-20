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
