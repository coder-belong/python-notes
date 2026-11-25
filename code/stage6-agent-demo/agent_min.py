# agent_min.py：最小的 Agent 循环
import json

from llm import MODEL, NO_THINKING, client
from tools import FUNCTIONS, TOOLS

MAX_STEPS = 10   # 最多调几次模型：防止模型一直调工具停不下来


def run_agent(task: str) -> str:
    messages = [
        {"role": "system", "content": "你是个人助手，可以调用工具完成任务。需要数字计算时用 calculate，不要自己心算。"},
        {"role": "user", "content": task},
    ]
    for step in range(1, MAX_STEPS + 1):
        # ① 思考：把目前为止的全部消息发给模型，让它决定下一步
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, extra_body=NO_THINKING)
        msg = resp.choices[0].message
        messages.append(msg)                       # 模型这一步说的话（含要调哪些工具）放进历史

        if not msg.tool_calls:                     # 不调工具了：说明它认为任务完成，这就是最终回答
            print(f"第 {step} 步：完成")
            return msg.content

        for call in msg.tool_calls:                # ② 行动：执行模型要调的每个工具
            args = json.loads(call.function.arguments)
            result = FUNCTIONS[call.function.name](**args)
            print(f"第 {step} 步：{call.function.name}({str(args)[:60]}) → {result}")   # 参数太长只显示前 60 个字
            # ③ 观察：工具结果放回历史，下一轮模型就能看到
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)})

    return "步数用完了，任务没完成"


if __name__ == "__main__":
    print(run_agent("明天北京和上海的最高气温差几度？发邮件告诉小王，提醒他出差带合适的衣服。"))
