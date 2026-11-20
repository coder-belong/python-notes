class Counter:
    def __init__(self, name: str, start: int = 0) -> None:   # 创建对象时自动调用
        self.name = name          # self 就是「这个对象自己」
        self.count = start

    def add(self, n: int = 1) -> None:    # 方法的第一个参数都是 self
        self.count += n

    def __repr__(self) -> str:            # print 对象时显示什么
        return f"Counter({self.name}={self.count})"


c = Counter("clicks")
c.add()
c.add(5)
print(c.count)     # 6
print(c)           # Counter(clicks=6)
