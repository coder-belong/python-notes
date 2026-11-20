score = 85
if score >= 90:
    level = "A"
elif score >= 60:          # 注意是 elif
    level = "B"
else:
    level = "C"
print(level)               # B

# 一行版（三元表达式）
status = "及格" if score >= 60 else "不及格"

# 逻辑运算用英文单词
if score > 60 and score < 90:
    print("中等")
if not False:
    print("not 是取反")

# 判断 None 用 is
x = None
if x is None:
    print("x 没有值")

# ---- 真假值 ----
items = []
if not items:              # 空列表算假，not 取反后为真
    print("列表是空的")

if items:                  # 反过来：不为空
    print("列表里有东西")

# ---- 循环 ----
for i in range(3):            # 0 1 2
    print(i)

for i in range(1, 10, 2):     # 1 3 5 7 9：起点、终点（不含）、步长
    print(i, end=" ")
print()

n = 0
while n < 3:
    n += 1                    # Python 没有 n++

for i in range(10):
    if i == 2:
        continue              # 跳过这一次
    if i == 4:
        break                 # 结束整个循环
    print(i)                  # 0 1 3
