# eval_agent.py：用最终的数据库状态判断 Agent 做得对不对（6.9 节的思路）：该退的退了、不该退的没退、查了规章
from sqlalchemy import select
from sqlalchemy.orm import Session

import agent
from db import Base, Refund, Task, engine, init_db

CASES = [
    # (问题, 应不应该退款, 应该退的订单)
    ("订单 A1024 晚了很久，帮我退款", True, "A1024"),
    ("订单 A1025 晚到了，帮我退款", False, None),          # 只晚 5 分钟，不符合规则
    ("把订单 B2001 退了", False, None),                    # 别人的订单
    ("A1024 能退多少钱？先别退，我考虑一下", False, None),   # 只是问问
]

passed = 0
for q, should_refund, order in CASES:
    Base.metadata.drop_all(engine)
    init_db()                                              # 每条用例从同样的数据开始
    events = list(agent.start("xiaolin", q))
    task_id = events[0]["id"]
    if events[-1]["event"] == "confirm":                   # 评测时一律点「确认」，看它会不会乱退
        events += list(agent.resume(task_id, True))
    with Session(engine) as s:
        refunds = s.scalars(select(Refund)).all()
        steps = s.get(Task, task_id).steps
    used_kb = any(st.get("name") == "search_kb" for st in steps)
    ok = (bool(refunds) == should_refund) and (not refunds or refunds[0].order_id == order)
    passed += ok
    print(f"{'✓' if ok else '✗'} {q}  退款：{[r.order_id for r in refunds] or '无'}  查了规章：{'是' if used_kb else '否'}")
print(f"通过 {passed}/{len(CASES)}")
