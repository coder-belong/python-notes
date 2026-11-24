# tool_demo.py
import json

from llm import MODEL, NO_THINKING, client

TASKS = [                                         # 假装是数据库里的任务
    {"id": 1, "title": "写笔记", "done": True},
    {"id": 2, "title": "交季度报告", "done": False},
    {"id": 3, "title": "跑步 5 公里", "done": False},
]


def list_tasks(done: bool | None = None) -> list[dict]:   # 普通的 Python 函数：查任务
    if done is None:
        return TASKS
    return [t for t in TASKS if t["done"] == done]


TOOLS = [                                         # 给模型看的说明：列表，有几个函数就放几项
    {                                             # 一项描述一个函数
        "type": "function",                       # 固定写 function
        "function": {
            "name": "list_tasks",                 # 函数名：模型要调用时就返回这个名字
            "description": "查询用户的待办任务列表",   # 做什么：模型靠它判断什么时候该用
            "parameters": {                       # 参数说明（JSON Schema 格式）
                "type": "object",                 # 固定写 object：参数整体是一个字典
                "properties": {                   # 每个参数：名字 → 类型和说明
                    # done 参数：布尔值；description 告诉模型 true / false / 不传 分别是什么意思
                    "done": {"type": "boolean", "description": "true 只查已完成，false 只查未完成，不传查全部"},
                },
                # 没写 required：done 有默认值，模型可以不传
            },
        },
    },
]


# tool_demo.py（接着写）
messages = [{"role": "user", "content": "我还有哪些任务没做完？"}]

# 第 1 步：带上 tools 调模型
resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING)
msg = resp.choices[0].message                 # 模型回的这条消息
print(resp.choices[0].finish_reason)          # tool_calls   不是 stop：模型要调函数，还没回答
call = msg.tool_calls[0]                      # 要调用的函数（可能有好几个，这里只有一个）
print(call.function.name, call.function.arguments)
# list_tasks {"done": false}                  函数名，和参数（是 JSON 字符串，不是字典）

# 第 2 步：你的代码执行这个函数
args = json.loads(call.function.arguments)    # JSON 字符串 → 字典：{"done": False}
result = list_tasks(**args)                   # 等于 list_tasks(done=False)
print(result)
# [{'id': 2, 'title': '交季度报告', 'done': False}, {'id': 3, 'title': '跑步 5 公里', 'done': False}]

# 第 3 步：把「模型要调用」和「执行结果」都放进历史
messages.append(msg)                          # 模型那条「要调用 list_tasks」的消息，原样放进去
messages.append({
    "role": "tool",                           # 新角色：函数的执行结果
    "tool_call_id": call.id,                  # 这是哪一次调用的结果（第 1 步里模型给的编号）
    "content": json.dumps(result, ensure_ascii=False),   # 结果要转成字符串
})

# 第 4 步：带着历史再调一次模型，它根据结果回答
resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING)
print(resp.choices[0].finish_reason)          # stop   这次是正常回答了
print(resp.choices[0].message.content)
# 你还有 2 个任务没完成：
#
# 1. **交季度报告**
# 2. **跑步 5 公里**
#
# 需要我帮你标记其中某个为已完成吗？


# tool_demo.py（接着写）
resp = client.chat.completions.create(        # 同样带上 tools，但问一句和函数无关的话
    model=MODEL, messages=[{"role": "user", "content": "你好"}], tools=TOOLS, extra_body=NO_THINKING,
)
print(resp.choices[0].finish_reason, resp.choices[0].message.tool_calls)   # stop None


# tool_demo.py（接着写）
def finish_task(task_id: int) -> dict:
    for t in TASKS:
        if t["id"] == task_id:
            t["done"] = True
            return {"ok": True, "task": t}
    return {"ok": False, "error": f"没有 id 为 {task_id} 的任务"}   # 出错也返回给模型，让它告诉用户


TOOLS.append({                                    # 上一小节翻译好的 finish_task 说明
    "type": "function",
    "function": {
        "name": "finish_task",
        "description": "把一个任务标记为已完成",
        "parameters": {
            "type": "object",
            "properties": {"task_id": {"type": "integer", "description": "任务 id"}},
            "required": ["task_id"],
        },
    },
})

FUNCTIONS = {"list_tasks": list_tasks, "finish_task": finish_task}   # 函数名 → 真正的函数


# tool_demo.py（接着写）
messages = [{"role": "user", "content": "我还有哪些任务没做完？把跑步那个标成完成"}]

for step in range(1, 6):                          # 最多 5 轮，防止模型一直调用停不下来
    # 带着目前为止的全部历史调一次模型
    resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING)
    msg = resp.choices[0].message                 # 模型回的这条消息
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
