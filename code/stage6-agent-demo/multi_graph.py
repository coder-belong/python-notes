# multi_graph.py：多 Agent：Planner 拆步骤 → Executor 查资料 → Writer 写 → Reviewer 检查，不合格按问题打回给对应的角色
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent import run_agent
from lc_llm import llm


class State(TypedDict):   # 共享状态：三个角色都读写这一份
    task: str
    plan: list[str]
    results: Annotated[list[str], operator.add]   # Annotated + operator.add：节点返回的列表追加进去，而不是覆盖
    report: str
    feedback: str
    target: str     # 打回给谁：writer（只是文字问题）/ planner（资料不够，要重新查）
    round: int


class Plan(BaseModel):
    steps: list[str]


class Review(BaseModel):
    passed: bool
    problems: list[str]
    need_more_data: bool   # 是不是缺资料：缺资料要重新规划，只是写得不好就让 Writer 改


def planner(state: State) -> dict:
    extra = f"\n上一版被打回，问题：{state['feedback']}。这次的计划要补上缺的信息。" if state["feedback"] else ""
    plan = llm.with_structured_output(Plan, method="function_calling").invoke(
        f"把任务拆成 2～4 个步骤，每步一句话。可用能力：查北京/上海/广州明天的天气、计算。只拆查资料和计算的步骤，写成稿是 Writer 的事。\n任务：{state['task']}{extra}"
    )
    print(f"[Planner 第 {state['round'] + 1} 轮] {plan.steps}")
    return {"plan": plan.steps}


def executor(state: State) -> dict:
    new = []
    for step in state["plan"]:   # 每一步交给 6.2 节的单 Agent 去做
        answer, _ = run_agent(f"已知：{state['results'] + new}\n只做这一步：{step}", confirm=lambda *_: False, log=lambda _: None)
        new.append(f"{step}：{answer}")
        print(f"[Executor] {step} ✓")
    return {"results": new}


def writer(state: State) -> dict:
    extra = f"\n上一稿：{state['report']}\n审核意见：{state['feedback']}\n按意见修改。" if state["feedback"] else ""
    report = llm.invoke(f"任务：{state['task']}\n资料：{state['results']}{extra}\n只输出成稿本身。").content
    print(f"[Writer 第 {state['round'] + 1} 稿] {report}")
    return {"report": report, "round": state["round"] + 1}


def reviewer(state: State) -> dict:
    review = llm.with_structured_output(Review, method="function_calling").invoke(
        f"任务：{state['task']}\n资料：{state['results']}\n成稿：{state['report']}\n"
        "逐条检查成稿是否满足任务的每个要求、数字是否和资料一致。全部满足 passed=true。"
        "资料里缺信息才 need_more_data=true。"
    )
    if len(state["report"]) > 45:   # 字数交给代码判断（6.10 节：模型数不准）
        review.passed = False
        n = len(state["report"])
        review.problems.append(f"超过 45 字：现在 {n} 字，至少要删掉 {n - 45} 个字")   # 意见要具体到「改多少」
    print(f"[Reviewer] {'通过' if review.passed else '打回：' + '；'.join(review.problems)}")
    target = "planner" if review.need_more_data else "writer"
    return {"feedback": "" if review.passed else "；".join(review.problems), "target": target}


def route(state: State) -> str:   # 条件边：通过就结束；超过 3 稿也结束（交给人）；否则打回给对应的角色
    if not state["feedback"] or state["round"] >= 3:
        return END
    return state["target"]


g = StateGraph(State)
g.add_node("planner", planner)
g.add_node("executor", executor)
g.add_node("writer", writer)
g.add_node("reviewer", reviewer)
g.add_edge(START, "planner")
g.add_edge("planner", "executor")
g.add_edge("executor", "writer")
g.add_edge("writer", "reviewer")
g.add_conditional_edges("reviewer", route)
app = g.compile()

final = app.invoke({"task": "给小王写一条天气简报：北京、上海、广州明天的天气和最高最低气温，指出哪个城市昼夜温差最大、温差几度，再给一句穿衣建议，45 字以内。",
                    "plan": [], "results": [], "report": "", "feedback": "", "target": "", "round": 0})
print("\n最终：", final["report"])
