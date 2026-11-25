# plan_agent.py：先规划再执行（Plan-and-Execute）
import json

from pydantic import BaseModel

from agent import run_agent
from llm import MODEL, NO_THINKING, client


class Plan(BaseModel):
    steps: list[str]   # 每一步是一句能独立完成的小任务


PLANNER = """你是规划助手。把用户的任务拆成 2～5 个按顺序执行的小步骤，每步一句话，能独立完成。
可用的能力：查北京 / 上海 / 广州明天的天气、做数学计算、发邮件。
只输出 json：{"steps": ["第一步", "第二步"]}"""


def make_plan(task: str) -> Plan:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": PLANNER}, {"role": "user", "content": task}],
        response_format={"type": "json_object"},   # 4.4 节的 JSON 模式
        extra_body=NO_THINKING,
    )
    return Plan.model_validate_json(resp.choices[0].message.content)


def plan_and_execute(task: str) -> str:
    plan = make_plan(task)
    print("计划：")
    for i, s in enumerate(plan.steps, 1):
        print(f"  {i}. {s}")

    done: list[str] = []   # 已完成步骤的结果，后面的步骤要用
    for i, step in enumerate(plan.steps, 1):
        context = "\n".join(done) or "无"
        # 每一步交给 6.2 节的 run_agent 去做：它只看到这一小步 + 前面的结果，不用管整个任务
        result, _ = run_agent(f"已完成的步骤结果：\n{context}\n\n现在只做这一步：{step}",
                              confirm=lambda *_: True, log=lambda _: None)
        print(f"  ✓ 第 {i} 步：{result[:60]!r}")
        done.append(f"第 {i} 步（{step}）：{result}")

    # 最后汇总成给用户的回答
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"任务：{task}\n各步骤结果：\n" + "\n".join(done) + "\n\n用两三句话告诉用户结果。"}],
        extra_body=NO_THINKING,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    print(plan_and_execute("比较北京、上海、广州明天的最高气温，算出最热和最冷的城市差几度，发邮件告诉小王哪个城市最暖和。"))
