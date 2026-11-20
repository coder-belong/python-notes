from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)   # 列表、字典这种默认值要这样写


t = Task("写笔记")
t.tags.append("学习")
print(t)                           # Task(title='写笔记', done=False, tags=['学习'])
print(t == Task("写笔记", tags=["学习"]))   # True  按字段比较
