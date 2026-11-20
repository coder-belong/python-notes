# 故意演示报错：第一行就会抛 ValueError，后面两行不会执行
name, age = "Tom,18,北京".split(",")   # ValueError: too many values to unpack (expected 2)
name, age = "Tom".split(",")           # ValueError: not enough values to unpack (expected 2, got 1)

name, rest = "Tom,18,北京".split(",", 1)   # 只在第一个逗号处切：'Tom'、'18,北京'
