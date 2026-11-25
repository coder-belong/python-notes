# agent.py：在 agent_min.py 的基础上补齐：参数校验、工具出错、人工确认、Trace 和成本
import json
import time
from collections.abc import Callable

from pydantic import BaseModel, ValidationError

from llm import MODEL, NO_THINKING, client
from tools import FUNCTIONS, TOOLS

SYSTEM = "你是个人助手，可以调用工具完成任务。需要数字计算时用 calculate，不要自己心算。"
MAX_STEPS = 8    # 最多调几次模型
MAX_FAILS = 2    # 工具一共失败几次就停：别让模型无限重试
RISKY = {"send_email"}   # 高风险工具：执行前要用户确认
PRICE = {"hit": 0.006, "miss": 0.3, "output": 1.2}   # 美元 / 百万 token，和 4.3 节一样


class WeatherArgs(BaseModel):   # 每个工具的参数各写一个模型，用来校验模型给的参数（3.3 节的写法）
    city: str


class CalcArgs(BaseModel):
    expression: str


class EmailArgs(BaseModel):
    to: str
    content: str


ARGS = {"get_weather": WeatherArgs, "calculate": CalcArgs, "send_email": EmailArgs}


def cost_usd(u) -> float:
    return (u.prompt_cache_hit_tokens * PRICE["hit"] + u.prompt_cache_miss_tokens * PRICE["miss"]
            + u.completion_tokens * PRICE["output"]) / 1_000_000


def run_tool(name: str, raw_args: str, confirm: Callable[[str, dict], bool]) -> tuple[bool, str]:
    """执行一个工具，返回（成功没有, 给模型看的结果）。出了任何错都不抛异常，而是把错误告诉模型。"""
    if name not in FUNCTIONS:                       # ① 模型编了一个不存在的工具
        return False, f"没有 {name} 这个工具"
    try:
        args = ARGS[name].model_validate_json(raw_args).model_dump()   # ② 参数先校验，不合格不执行
    except ValidationError as e:
        return False, f"参数不对：{e.errors()[0]['msg']}"
    if name in RISKY and not confirm(name, args):   # ③ 高风险操作先问用户
        return False, "用户拒绝了这个操作。不要再尝试，直接告诉用户没有执行"
    try:
        return True, json.dumps(FUNCTIONS[name](**args), ensure_ascii=False)
    except Exception as e:                          # ④ 工具自己出错（比如城市不支持）
        return False, f"出错：{e}"


def run_agent(task: str, confirm: Callable[[str, dict], bool], log: Callable[[str], None] = print,
              system: str = SYSTEM) -> tuple[str, list[dict]]:
    """跑一个任务，返回（最终回答, trace）。trace 是每一步的记录。system 可以换，6.9 节评测时用。"""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": task}]
    trace: list[dict] = []
    fails = 0
    for step in range(1, MAX_STEPS + 1):
        start = time.perf_counter()
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING)
        msg = resp.choices[0].message
        messages.append(msg)
        trace.append({   # 记下这一步：调了模型，花了多少时间、token、钱
            "step": step, "type": "llm", "ms": round((time.perf_counter() - start) * 1000),
            "tokens": resp.usage.total_tokens, "usd": cost_usd(resp.usage),
        })

        if not msg.tool_calls:
            return msg.content, trace

        for call in msg.tool_calls:
            start = time.perf_counter()
            ok, result = run_tool(call.function.name, call.function.arguments, confirm)
            trace.append({   # 记下这次工具调用：名字、参数、结果、成功没有
                "step": step, "type": "tool", "name": call.function.name, "args": call.function.arguments,
                "ok": ok, "result": result, "ms": round((time.perf_counter() - start) * 1000),
            })
            log(f"第 {step} 步：{call.function.name} {'✓' if ok else '✗'} {result[:50]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
            if not ok:
                fails += 1
                if fails >= MAX_FAILS:   # 失败太多次：停下来，交给人处理
                    return f"工具失败了 {fails} 次，任务先停下，请人工处理", trace

    return "步数用完了，任务没完成", trace


def ask_user(name: str, args: dict) -> bool:   # 命令行里问用户；网页里换成弹窗按钮（6.11 节）
    return input(f"    要执行 {name}({json.dumps(args, ensure_ascii=False)[:40]}…) 吗？(y/n) ").strip() == "y"


if __name__ == "__main__":
    answer, trace = run_agent("明天北京和深圳哪个更暖和？", confirm=ask_user)
    print(answer, "\n")

    answer, trace = run_agent("明天北京和上海的最高气温差几度？发邮件告诉小王。", confirm=ask_user)
    print(answer)
