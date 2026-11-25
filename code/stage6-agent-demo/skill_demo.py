# skill_demo.py：Skill：system 里只放每个 Skill 的名字和一句说明，用到时才把全文读进来
import json
from pathlib import Path

from llm import MODEL, NO_THINKING, client


def read_skills() -> dict[str, dict]:
    skills = {}
    for f in Path("skills").glob("*/SKILL.md"):            # 每个 Skill 一个文件夹，里面一个 SKILL.md
        text = f.read_text(encoding="utf-8")
        _, head, body = text.split("---", 2)                # 开头两个 --- 之间是名字和说明
        meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
        skills[meta["name"]] = {"description": meta["description"], "body": body.strip()}
    return skills


SKILLS = read_skills()
catalog = "\n".join(f"- {name}：{s['description']}" for name, s in SKILLS.items())
SYSTEM = f"你是办公助手。下面这些事有专门的写法说明，遇到时先调用 load_skill 读说明，再照着做：\n{catalog}"

LOAD_SKILL = {
    "type": "function",
    "function": {
        "name": "load_skill",
        "description": "读取某个 Skill 的完整说明",
        "parameters": {"type": "object", "properties": {"name": {"type": "string", "enum": list(SKILLS)}}, "required": ["name"]},
    },
}


def run(task: str) -> None:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}]
    while True:
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=[LOAD_SKILL], extra_body=NO_THINKING)
        msg = resp.choices[0].message
        print(f"  （这次输入 {resp.usage.prompt_tokens} token）")
        if not msg.tool_calls:
            print(msg.content)
            return
        messages.append(msg)
        for call in msg.tool_calls:
            name = json.loads(call.function.arguments)["name"]
            print(f"  读取 Skill：{name}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": SKILLS[name]["body"]})


print(SYSTEM, "\n")
run("帮我写本周周报：上线了登录页，修了 3 个 bug；接口文档还没写完；下周做支付页。")
print()
run("今天几号来着？")   # 和 Skill 无关：一个都不读
