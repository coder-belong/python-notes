# eval_agent.py：Agent 评测：同一组任务，比较三版 system 的成功率、步数、成本
from agent import run_agent

# 任务 + 怎么判断做对了（答案里要出现的内容）
CASES = [
    ("明天北京最高几度？", "6"),
    ("明天上海和广州的最高气温差几度？", "11"),
    ("北京明天的最高和最低气温差多少度？", "10"),
    ("明天广州和北京的最低气温差几度？", "21"),
    ("三个城市明天最高气温的平均值是多少？保留一位小数", "14.3"),
    ("明天深圳天气怎么样？", "广州"),   # 不支持深圳：应该说只有北京、上海、广州，不能编
]

VERSIONS = {
    "A 有计算规则": "你是个人助手，可以调用工具完成任务。需要数字计算时用 calculate，不要自己心算。",
    "B 没有规则": "你是个人助手，可以调用工具完成任务。",
    "C 少调工具": "你是个人助手，可以调用工具完成任务。能直接回答的就直接回答，尽量少调用工具，节省时间。",
}

for name, system in VERSIONS.items():
    passed, steps, usd, calc = 0, 0, 0.0, 0
    for task, expected in CASES:
        answer, trace = run_agent(task, confirm=lambda *_: False, log=lambda _: None, system=system)
        llm = [t for t in trace if t["type"] == "llm"]
        steps += len(llm)
        usd += sum(t["usd"] for t in llm)
        calc += any(t.get("name") == "calculate" for t in trace)   # 这个任务有没有用计算工具
        if expected in answer:
            passed += 1
        else:
            print(f"   ✗ {task} → {answer[:50]!r}")
    n = len(CASES)
    print(f"{name}：通过 {passed}/{n}，平均 {steps / n:.1f} 步，用了 calculate {calc} 次，共 ${usd:.5f}")
