# memory_long.py：长期记忆：重要的信息存进文件，下次新对话再读出来
import json
from pathlib import Path

from llm import MODEL, NO_THINKING, client

FILE = Path("memory.json")   # 真实项目里存数据库，按用户分开

REMEMBER = {   # 给模型一个「记下来」的工具
    "type": "function",
    "function": {
        "name": "remember",
        "description": "用户说了以后还用得上的个人信息、偏好（名字、过敏、口味、习惯）时，调用它记下来。已经知道的不要重复记",
        "parameters": {"type": "object", "properties": {"fact": {"type": "string"}}, "required": ["fact"]},
    },
}


def load() -> list[str]:
    return json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else []


def new_session(question: str) -> None:
    """每次都是一个全新的对话：历史是空的，只有记忆文件里的内容。"""
    memories = load()
    system = "你是生活助手，回答一两句话。" + (f"\n关于用户你已经知道：{'；'.join(memories)}" if memories else "")
    messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
    while True:   # 和 4.5 节一样：调了工具就把结果放回去，再问一次，直到模型直接回答
        msg = client.chat.completions.create(
            model=MODEL, messages=messages, tools=[REMEMBER], extra_body=NO_THINKING
        ).choices[0].message
        if not msg.tool_calls:
            break
        messages.append(msg)
        for call in msg.tool_calls:   # 模型决定要记：追加进文件
            fact = json.loads(call.function.arguments)["fact"]
            FILE.write_text(json.dumps(load() + [fact], ensure_ascii=False), encoding="utf-8")
            print(f"  [记下了] {fact}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": "已记下"})
    print(f"{question} → {msg.content}")


FILE.unlink(missing_ok=True)   # 演示：从空记忆开始
new_session("我是小林，对花生过敏，平时不吃辣。")
new_session("今天天气不错。")                        # 没什么要记的
new_session("推荐个下午吃的零食。")                  # 新对话，但记得过敏和口味
print(load())
