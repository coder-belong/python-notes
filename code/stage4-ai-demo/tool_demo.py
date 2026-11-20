# tool_demo.py
import json

from llm import MODEL, NO_THINKING, client

TASKS = [                                         # 假装是数据库里的任务
    {"id": 1, "title": "写笔记", "done": True},
    {"id": 2, "title": "交季度报告", "done": False},
    {"id": 3, "title": "跑步 5 公里", "done": False},
]


def list_tasks(done: bool | None = None) -> list[dict]:   # 普通的 Python 函数
    if done is None:
        return TASKS
    return [t for t in TASKS if t["done"] == done]


def finish_task(task_id: int) -> dict:
    for t in TASKS:
        if t["id"] == task_id:
            t["done"] = True
            return {"ok": True, "task": t}
    return {"ok": False, "error": f"没有 id 为 {task_id} 的任务"}   # 出错也返回给模型，让它告诉用户


TOOLS = [                                         # 给模型看的函数说明：名字、做什么、参数（JSON Schema 格式）
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "查询用户的待办任务列表",   # 模型靠 description 判断什么时候该用，要写清楚
            "parameters": {
                "type": "object",
                "properties": {
                    "done": {"type": "boolean", "description": "true 只查已完成，false 只查未完成，不传查全部"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "把一个任务标记为已完成",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "integer", "description": "任务 id"}},
                "required": ["task_id"],          # 必须传的参数
            },
        },
    },
]

FUNCTIONS = {"list_tasks": list_tasks, "finish_task": finish_task}   # 函数名 → 真正的函数，执行时按名字找


resp = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": "我还有哪些任务没做完？"}], tools=TOOLS, extra_body=NO_THINKING,
)
m = resp.choices[0].message
print(repr(m.content))           # '我来查一下你未完成的任务。'   可能带一句话，也可能是空的
for c in m.tool_calls:
    print(c.id, c.type, c.function.name, repr(c.function.arguments))
# call_00_yedAQk8XZOs2YqNUiXZn4849 function list_tasks '{"done": false}'
#   id：这次调用的编号，回传结果时要带上
#   arguments：参数是 JSON 字符串，要自己 json.loads


resp = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": "你好"}], tools=TOOLS, extra_body=NO_THINKING,
)
print(resp.choices[0].finish_reason, resp.choices[0].message.tool_calls)   # stop None


messages = [{"role": "user", "content": "我还有哪些任务没做完？把跑步那个标成完成"}]

for step in range(1, 6):                          # 最多 5 轮，防止模型一直调用停不下来
    resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING)
    msg = resp.choices[0].message
    print(f"第 {step} 次调用，finish_reason={resp.choices[0].finish_reason}")
    if not msg.tool_calls:                        # ① 不要调函数了：这就是最终回答
        print("最终回答：", msg.content)
        break
    messages.append(msg)                          # ② 模型「要调用」的这条消息，原样放进历史
    for call in msg.tool_calls:                   # ③ 一次可能要调好几个，逐个执行
        args = json.loads(call.function.arguments)                # 参数：JSON 字符串 → 字典
        print("  模型要调用：", call.function.name, args)
        result = FUNCTIONS[call.function.name](**args)            # 按名字找到函数，执行
        print("  执行结果：", result)
        messages.append({                                         # ④ 结果用 tool 角色放进历史
            "role": "tool",
            "tool_call_id": call.id,                              # 对应哪一次调用
            "content": json.dumps(result, ensure_ascii=False),    # 结果转成字符串
        })
    # 回到循环开头：带着函数结果再调一次模型
