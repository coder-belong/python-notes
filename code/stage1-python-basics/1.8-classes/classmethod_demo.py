class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @classmethod
    def from_text(cls, text: str) -> "User":    # cls 就是 User 这个类
        name, age = text.split(",")
        return cls(name, int(age))              # 等于 User(name, int(age))


u = User.from_text("Tom,18")
print(u.name, u.age)       # Tom 18
