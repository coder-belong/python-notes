with open("a.txt", "w", encoding="utf-8") as fp:
    fp.write("hi")
# 走到这里文件已经关了，等价于：
fp = open("a.txt", "w", encoding="utf-8")
try:
    fp.write("hi")
finally:
    fp.close()
