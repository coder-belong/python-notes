nums = [1, 2, 3, 4]

# ① 每个数算平方
squares = [n * n for n in nums]                 # [1, 4, 9, 16]

squares = []
for n in nums:
    squares.append(n * n)

# ② 带过滤条件：只要偶数
evens = [n for n in nums if n % 2 == 0]         # [2, 4]

evens = []
for n in nums:
    if n % 2 == 0:
        evens.append(n)

# ③ 从字典列表里取一个字段
rows = [{"id": 1, "name": "Tom"}, {"id": 2, "name": "Jerry"}]
names = [r["name"] for r in rows]               # ['Tom', 'Jerry']

names = []
for r in rows:
    names.append(r["name"])

# ④ 字典推导式：用 {键: 值}
by_id = {r["id"]: r["name"] for r in rows}      # {1: 'Tom', 2: 'Jerry'}

by_id = {}
for r in rows:
    by_id[r["id"]] = r["name"]

print(squares, evens, names, by_id)             # [1, 4, 9, 16] [2, 4] ['Tom', 'Jerry'] {1: 'Tom', 2: 'Jerry'}
