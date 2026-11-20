# 故意演示报错：运行到 c["name"] 那行会抛 TypeError，后面不再执行
from counter import Counter            # 补：Counter 定义在 counter.py（导入时会先执行 counter.py 里的打印）

c = Counter("clicks")                  # 对象
d = {"name": "clicks", "count": 0}     # 字典

c.name         # 'clicks'   对象：用点号
d["name"]      # 'clicks'   字典：用方括号
c["name"]      # TypeError: 'Counter' object is not subscriptable
d.name         # AttributeError: 'dict' object has no attribute 'name'

vars(c)        # {'name': 'clicks', 'count': 0}   对象转成字典
