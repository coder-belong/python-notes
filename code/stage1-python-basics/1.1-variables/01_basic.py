# 01_basic.py
name = "林必龙"          # str 字符串
age = 18                 # int 整数
price = 9.9              # float 小数
is_ok = True             # bool：True / False，首字母大写
nothing = None           # None：表示「没有值」

print(name, age, price, is_ok, nothing)   # 林必龙 18 9.9 True None
print(type(age))                          # <class 'int'>

# ---- 类型标注 ----
episode: int = 3
title: str = "试拍第一集"
note: str | None = None      # 可以是 str，也可以是 None

# ---- 缩进就是语法 ----
if age >= 18:
    print("成年")       # 缩进的部分属于 if
print("结束")           # 不缩进，if 结束了

# ---- 字符串 ----
user = "Tom"
n = 3
print(f"{user} 有 {n} 个任务")     # f-string：在字符串里嵌变量，最常用
print(f"{price:.2f}")              # 9.90 保留两位小数
print("a,b,c".split(","))          # ['a', 'b', 'c']
print("  hi  ".strip())            # 'hi' 去首尾空格
print("hello".upper(), "Hello".lower())   # HELLO hello
print("abc".startswith("a"))       # True

# ---- split 的第二个参数是最多切几刀 ----
full = "林 必 龙"
first, rest = full.split(" ", 1)    # 只切 1 刀 → ['林', '必 龙']
print(first, "|", rest)             # 林 | 必 龙

# ---- join 是 split 的反操作，replace 替换 ----
print("-".join(["a", "b", "c"]))       # a-b-c    用 - 把列表拼起来（元素必须是字符串）
print(", ".join(str(n) for n in [1, 2]))   # 1, 2   数字要先转成字符串
print("a.b.c".replace(".", "/"))       # a/b/c

# ---- 切片 [开始:结束:步长] ----
s = "abcdef"
print(s[1:3])     # bc      下标 1、2
print(s[:2])      # ab      从头开始
print(s[2:])      # cdef    到结尾
print(s[-2:])     # ef      最后两个
print(s[::2])     # ace     每隔一个取
print(s[::-1])    # fedcba  反过来
print(len(s))     # 6       长度

# ---- 数字 ----
print(7 / 2)     # 3.6   除法结果总是小数
print(7 // 2)    # 3     整除
print(7 % 2)     # 1     取余
print(2 ** 10)   # 1024  乘方
print(int("42") + 1, str(42) + "!")   # 43 42!  类型转换
