# ---- 列表 list：有顺序，可以改 ----
nums = [3, 1, 2]
nums.append(4)              # 末尾加 → [3, 1, 2, 4]
nums.remove(1)              # 删掉值为 1 的 → [3, 2, 4]
print(nums[0], nums[-1])    # 3 4      -1 是最后一个
print(nums[0:2])            # [3, 2]   切片，含头不含尾
print(len(nums))            # 3
print(sorted(nums))         # [2, 3, 4] 返回新列表
print(2 in nums)            # True

# ---- 字典 dict：键值对 ----
user = {"name": "Tom", "age": 18}
print(user["name"])               # Tom
print(user.get("email"))          # None   键不存在不报错
print(user.get("email", "无"))    # 无     给默认值
user["age"] = 19                  # 改
user["email"] = "t@x.com"         # 加
del user["email"]                 # 删
print("name" in user)             # True   判断键是否存在

for key, value in user.items():   # items() 同时拿到键和值
    print(key, value)
for key in user:                  # 直接遍历拿到的是键
    print(key)

# ---- 元组 tuple：和列表像，但不能改 ----
point = (3, 4)
x, y = point          # 拆包：按位置赋值
print(x, y)           # 3 4
a, b = 1, 2
a, b = b, a           # 交换两个变量

# ---- 拆包 ----
name, age = "Tom,18".split(",")   # split 先得到 ['Tom', '18']，再拆给两个变量
print(name, age)                  # Tom 18   注意 age 是字符串 '18'，要算数得 int(age)

first, *rest = [1, 2, 3, 4]       # 带 * 的接住剩下所有值，得到一个列表
print(first, rest)                # 1 [2, 3, 4]

_, age = ["Tom", 18]              # 用不到的值习惯用 _ 占位

# ---- 集合 set：不重复 ----
tags = {"a", "b", "a"}
print(tags)                       # {'a', 'b'}（顺序不固定）
print(set([1, 1, 2]))             # {1, 2}   给列表去重

# ---- 几个好用的遍历函数 ----
names = ["Tom", "Jerry"]
for index, name in enumerate(names):     # 带上序号，注意序号在前
    print(index, name)                    # 0 Tom / 1 Jerry

ages = [18, 20]
for name, age in zip(names, ages):       # 两个列表一一配对
    print(name, age)                      # Tom 18 / Jerry 20
