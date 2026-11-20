names = ["Tom", "Jerry"]
ages = [18, 20]

# 名字当键、年龄当值：一个字典
print(dict(zip(names, ages)))            # {'Tom': 18, 'Jerry': 20}

# 每个人一个字典：字典列表（接口返回数据最常用）
users = []
for name, age in zip(names, ages):
    users.append({"name": name, "age": age})
print(users)                             # [{'name': 'Tom', 'age': 18}, {'name': 'Jerry', 'age': 20}]

# 再带上从 1 开始的序号：enumerate 的 start 参数
users = []
for i, name in enumerate(names, start=1):
    users.append({"id": i, "name": name, "age": ages[i - 1]})
print(users[1])                          # {'id': 2, 'name': 'Jerry', 'age': 20}
