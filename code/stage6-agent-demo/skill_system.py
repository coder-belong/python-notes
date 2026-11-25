# skill_system.py：Skill 多了以后：注册（带版本）、检索、编排（一个任务用几个 Skill）
import json
from pathlib import Path

from llm import MODEL, NO_THINKING, client


# ---------- 注册：扫描 skill_lib/名字/版本/SKILL.md ----------
def parse(path: Path) -> dict:
    _, head, body = path.read_text(encoding="utf-8").split("---", 2)
    meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
    return {**meta, "body": body.strip()}


REGISTRY: dict[str, dict[str, dict]] = {}   # {名字: {版本: skill}}
for f in Path("skill_lib").glob("*/*/SKILL.md"):
    s = parse(f)
    REGISTRY.setdefault(s["name"], {})[s["version"]] = s


def get(name: str, pinned: dict[str, str]) -> dict:
    """取一个 Skill：锁了版本就用锁定的，否则用最新的。"""
    versions = REGISTRY[name]
    v = pinned.get(name) or max(versions, key=lambda x: tuple(map(int, x.split("."))))   # "1.10" 比 "1.9" 新，要按数字比
    return versions[v]


# ---------- 检索：Skill 太多时，只把相关的几个放进 system ----------
def bigrams(text: str) -> set[str]:
    return {text[i : i + 2] for i in range(len(text) - 1)}   # 相邻两个字一组：「周报」「报整」……


def search(task: str, k: int = 3) -> list[str]:
    scores = {}
    for name in REGISTRY:
        s = get(name, {})
        scores[name] = len(bigrams(task) & bigrams(s["description"] + " " + s["tags"]))   # 共同的两字组越多越相关
    return [n for n, sc in sorted(scores.items(), key=lambda x: -x[1])[:k] if sc > 0]


# ---------- 编排：模型按需加载，一个任务可以用好几个 ----------
def run(task: str, pinned: dict[str, str] | None = None) -> str:
    pinned = pinned or {}
    names = search(task)
    print("检索到：", names)
    catalog = "\n".join(f"- {n}：{get(n, pinned)['description']}" for n in names)
    system = f"你是办公助手。下面这些事有写法说明，用到哪个先调用 load_skill 读哪个，可以读多个：\n{catalog}"
    tool = {"type": "function", "function": {
        "name": "load_skill", "description": "读取某个 Skill 的完整说明",
        "parameters": {"type": "object", "properties": {"name": {"type": "string", "enum": names}}, "required": ["name"]},
    }}
    messages = [{"role": "system", "content": system}, {"role": "user", "content": task}]
    while True:
        msg = client.chat.completions.create(model=MODEL, messages=messages, tools=[tool], extra_body=NO_THINKING).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            s = get(json.loads(call.function.arguments)["name"], pinned)
            print(f"  加载 {s['name']}@{s['version']}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": s["body"]})


if __name__ == "__main__":
    print("已注册：", {n: sorted(v) for n, v in REGISTRY.items()})
    TASK = "把这周的周报整理一下，用邮件发给王经理：上线了登录页，修了 3 个 bug；接口文档没写完，需要后端配合；下周做支付页。"
    print(run(TASK, pinned={"weekly-report": "1.0"}), "\n")
    print(run(TASK))   # 不锁版本：用最新的 1.1
