# failure_demo.py：两种常见故障，从 Trace 里看出来，再改掉
import json

from llm import MODEL, NO_THINKING, client
import tools as t


def mini_agent(task: str, tools: list[dict], functions: dict) -> None:
    """最小循环，打印每一步的输入 token 和工具结果（就是一份简单的 Trace）。"""
    messages = [{"role": "user", "content": task}]
    for step in range(1, 6):
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools, extra_body=NO_THINKING)
        msg = resp.choices[0].message
        print(f"  第 {step} 步 输入 {resp.usage.prompt_tokens} token", end="")
        if not msg.tool_calls:
            print(f"  回答：{msg.content.replace(chr(10), ' ')[:60]}")
            return
        messages.append(msg)
        for call in msg.tool_calls:
            try:
                result = json.dumps(functions[call.function.name](**json.loads(call.function.arguments)), ensure_ascii=False)
            except Exception as e:
                result = str(e)
            print(f"  {call.function.name}({call.function.arguments}) → {result[:40]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})


def schema(name: str, desc: str, props: dict) -> dict:
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": list(props)}}}


WEATHER_TOOL = [schema("get_weather", "查城市明天的天气", {"city": {"type": "string"}})]

# ---------- 故障一：报错信息太含糊，模型不知道怎么改 ----------
def weather_vague(city: str) -> dict:
    if city not in t.WEATHER:
        raise ValueError("查询失败")                       # 只说失败，不说为什么
    return t.WEATHER[city]


def weather_clear(city: str) -> dict:
    if city not in t.WEATHER:
        raise ValueError(f"没有「{city}」，城市名只能是：{'、'.join(t.WEATHER)}（不带「市」）")   # 说清楚错在哪、正确的是什么
    return t.WEATHER[city]


print("故障一：报错含糊")
mini_agent("Is it cold in Beijing tomorrow? 用中文回答", WEATHER_TOOL, {"get_weather": weather_vague})
print("改：报错说清楚")
mini_agent("Is it cold in Beijing tomorrow? 用中文回答", WEATHER_TOOL, {"get_weather": weather_clear})


# ---------- 故障二：工具返回太长，上下文一下子撑大 ----------
LOGS = [f"2026-11-25 10:{i // 60:02d}:{i % 60:02d} INFO 请求正常 id={i}" for i in range(3000)]
LOGS[2345] = "2026-11-25 10:39:05 ERROR 数据库连接超时 id=2345"
LOG_TOOL = [schema("read_logs", "读取今天的服务日志", {"keyword": {"type": "string", "description": "可选，只看包含这个词的行，不需要就传空字符串"}})]


def read_logs_all(keyword: str = "") -> str:
    return "\n".join(LOGS)                                 # 不管要什么，全部返回


def read_logs_filtered(keyword: str = "") -> str:
    lines = [line for line in LOGS if keyword in line] if keyword else LOGS
    head = "\n".join(lines[:20])                           # 最多给 20 行
    return head + (f"\n……还有 {len(lines) - 20} 行，用 keyword 缩小范围（比如 ERROR）" if len(lines) > 20 else "")


print("\n故障二：工具结果太长")
mini_agent("今天服务日志里有没有报错？", LOG_TOOL, {"read_logs": read_logs_all})
print("改：截断 + 提示怎么缩小范围")
mini_agent("今天服务日志里有没有报错？", LOG_TOOL, {"read_logs": read_logs_filtered})


def read_logs_fixed(keyword: str = "") -> str:
    lines = [line for line in LOGS if keyword.lower() in line.lower()]   # 不区分大小写：模型传 error 也能匹配 ERROR
    if not lines:
        return f"没有包含「{keyword}」的行（共 {len(LOGS)} 行日志）"         # 空结果也要说清楚，别返回空字符串
    head = "\n".join(lines[:20])
    return head + (f"\n……还有 {len(lines) - 20} 行，用 keyword 缩小范围（比如 ERROR）" if len(lines) > 20 else "")


print("再改：不区分大小写、空结果说清楚")
mini_agent("今天服务日志里有没有报错？", LOG_TOOL, {"read_logs": read_logs_fixed})
