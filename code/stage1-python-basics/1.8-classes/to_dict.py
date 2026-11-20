from dataclasses import asdict, dataclass

from pydantic import BaseModel


@dataclass
class Point:
    x: int
    y: int


p = Point(1, 2)
print(p.x)              # 1                  点号取值
print(asdict(p))        # {'x': 1, 'y': 2}   dataclass 用 asdict() 转字典


class User(BaseModel):
    name: str
    age: int


u = User(name="Tom", age=18)
print(u.name)           # Tom                点号取值
print(u.model_dump())   # {'name': 'Tom', 'age': 18}   pydantic 用 .model_dump() 转字典
