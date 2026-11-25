# perm_demo.py：工具按权限分级：不同角色的用户，Agent 能用的工具不一样
import json

from llm import MODEL, NO_THINKING, client
from tools import FUNCTIONS, TOOLS

LEVEL = {"get_weather": "read", "calculate": "read", "send_email": "write"}   # 每个工具的权限级别
ROLE_CAN = {"guest": {"read"}, "member": {"read", "write"}}                  # 每个角色能用哪些级别


def tools_for(role: str) -> list[dict]:
    """第一道：只把这个角色能用的工具告诉模型。模型看不到的工具，就不会去调。"""
    return [t for t in TOOLS if LEVEL[t["function"]["name"]] in ROLE_CAN[role]]


def call_tool(role: str, name: str, args: dict) -> str:
    """第二道：执行前再查一次。模型可能编出一个没给它的工具名，不能只靠第一道。"""
    if LEVEL.get(name) not in ROLE_CAN[role]:
        return f"没有权限：{role} 不能使用 {name}"
    return json.dumps(FUNCTIONS[name](**args), ensure_ascii=False)


def run(role: str, task: str) -> None:
    tools = tools_for(role)
    print(f"[{role}] 可用工具：{[t['function']['name'] for t in tools]}")
    messages = [{"role": "system", "content": "你是个人助手，用工具完成任务。"}, {"role": "user", "content": task}]
    for _ in range(5):
        msg = client.chat.completions.create(model=MODEL, messages=messages, tools=tools, extra_body=NO_THINKING).choices[0].message
        if not msg.tool_calls:
            print("   ", msg.content.replace("\n", " ")[:80])
            return
        messages.append(msg)
        for call in msg.tool_calls:
            result = call_tool(role, call.function.name, json.loads(call.function.arguments))
            print(f"    调用 {call.function.name} → {result[:40]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})


TASK = "查一下明天上海天气，发邮件告诉小王。"
run("guest", TASK)
run("member", TASK)
print(call_tool("guest", "send_email", {"to": "小王", "content": "hi"}))   # 就算模型硬要调，第二道也拦住
