class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name}: ？"   # 普通动物不知道怎么叫


class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name)     # 先让父类把 name 设好
        self.breed = breed

    def speak(self) -> str:        # 覆盖父类方法
        return f"{self.name}: 汪"


print(Dog("旺财", "柴犬").speak())   # 旺财: 汪


# ---- 多态 ----
class Cat(Animal):
    def speak(self) -> str:        # 没写 __init__：直接用父类的
        return f"{self.name}: 喵"


# list[Animal]：列表里放的都是 Animal，子类的对象也算
animals: list[Animal] = [Dog("旺财", "柴犬"), Cat("咪咪"), Animal("某某")]
for a in animals:
    print(a.speak())    # 先在对象自己的类里找 speak，找不到再去父类找
# 旺财: 汪
# 咪咪: 喵
# 某某: ？

# ---- isinstance ----
d = Dog("旺财", "柴犬")
print(isinstance(d, Dog))       # True
print(isinstance(d, Animal))    # True   子类的对象也算父类
print(isinstance(d, Cat))       # False
print(type(d).__name__)         # Dog

# ---- 抽象基类 ----
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> None: ...   # 只规定要有这个方法，不写实现


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def save(self, key: str, value: str) -> None:
        self.data[key] = value


s = MemoryStorage()
s.save("a", "1")
print(s.data)          # {'a': '1'}
# Storage()            # 报错：抽象类不能直接创建对象


# ---- 鸭子类型 ----
class Robot:                   # 没有继承 Animal
    def speak(self) -> str:
        return "哔"


for a in [Dog("旺财", "柴犬"), Robot()]:
    print(a.speak())           # 旺财: 汪 / 哔
