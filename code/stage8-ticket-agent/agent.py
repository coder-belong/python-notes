# agent.py：Agent 循环（6.2 节的写法）+ 每一步存进数据库 + 高风险工具停下等人确认
import json
import time
from collections.abc import Iterator

from pydantic import ValidationError
from sqlalchemy.orm import Session

from db import Task, engine
from llm import MODEL, NO_THINKING, client
from tools import SCHEMAS, TOOLS

SYSTEM = """你是豆豆咖啡的客服 Agent，帮用户处理售后问题。
- 涉及规则（能不能退、怎么算）先用 search_kb 查规章，按规章办，不要凭印象
- 涉及订单先用 get_order 查实际情况
- 符合规则才调用 refund_order；不符合就说明原因
- 回答简短，说清楚依据"""
MAX_STEPS = 8
PRICE = {"hit": 0.006, "miss": 0.3, "output": 1.2}   # 美元 / 百万 token（4.3 节）


def event(kind: str, **data) -> dict:
    return {"event": kind, **data}


def run_tool(user: str, name: str, raw: str) -> tuple[bool, str]:
    """执行工具：参数先校验，出错不抛异常，把原因告诉模型（6.2 节）。"""
    if name not in TOOLS:
        return False, f"没有 {name} 这个工具"
    fn, model, _ = TOOLS[name]
    try:
        return True, json.dumps(fn(user, model.model_validate_json(raw)), ensure_ascii=False)
    except ValidationError as e:
        return False, f"参数不对：{e.errors()[0]['msg']}"
    except Exception as e:
        return False, f"出错：{e}"


def drive(task_id: int) -> Iterator[dict]:
    """从任务当前的状态接着跑，每做一件事 yield 一个事件。新任务、确认后继续，走的都是这里。"""
    with Session(engine) as s:
        task = s.get(Task, task_id)
        for step in range(len([x for x in task.steps if x["type"] == "llm"]) + 1, MAX_STEPS + 1):
            yield event("thinking", step=step)
            start = time.perf_counter()
            resp = client.chat.completions.create(model=MODEL, messages=task.messages, tools=SCHEMAS, extra_body=NO_THINKING)
            msg, u = resp.choices[0].message, resp.usage
            usd = (u.prompt_cache_hit_tokens * PRICE["hit"] + u.prompt_cache_miss_tokens * PRICE["miss"]
                   + u.completion_tokens * PRICE["output"]) / 1e6
            task.steps = [*task.steps, {"type": "llm", "step": step, "ms": round((time.perf_counter() - start) * 1000),
                                        "tokens": u.total_tokens, "usd": usd}]
            task.messages = [*task.messages, msg.model_dump(exclude_none=True)]

            if not msg.tool_calls:
                task.status, task.answer = "done", msg.content
                s.commit()
                yield event("final", text=msg.content, cost=round(sum(x.get("usd", 0) for x in task.steps), 6))
                return

            for call in msg.tool_calls:
                name, raw = call.function.name, call.function.arguments
                if TOOLS.get(name, (None, None, False))[2]:
                    # 高风险：先存下来，状态改成等确认，这次就到这里；用户确认后从 resume() 接着跑
                    task.status, task.pending = "waiting_confirm", {"id": call.id, "name": name, "args": raw}
                    s.commit()
                    yield event("confirm", tool=name, args=json.loads(raw))
                    return
                yield event("tool_start", tool=name, args=json.loads(raw))
                ok, result = run_tool(task.user, name, raw)
                task.steps = [*task.steps, {"type": "tool", "step": step, "name": name, "ok": ok}]
                task.messages = [*task.messages, {"role": "tool", "tool_call_id": call.id, "content": result}]
                yield event("tool_end", tool=name, ok=ok, result=result[:80])
            s.commit()   # 每一步都存：服务这时候重启，也能从这里接着跑
        task.status = "failed"
        s.commit()
        yield event("final", text="步数用完了，已转人工处理")


def start(user: str, question: str) -> Iterator[dict]:
    with Session(engine) as s:
        task = Task(user=user, question=question,
                    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}])
        s.add(task)
        s.commit()
        task_id = task.id
    yield event("task", id=task_id)
    yield from drive(task_id)


def resume(task_id: int, approve: bool) -> Iterator[dict]:
    """用户点了确认 / 拒绝：执行（或不执行）那个工具，把结果放进历史，接着跑。"""
    with Session(engine) as s:
        task = s.get(Task, task_id)
        if task is None or task.status != "waiting_confirm":
            yield event("error", msg="这个任务不在等确认")
            return
        p = task.pending
        if approve:
            ok, result = run_tool(task.user, p["name"], p["args"])
        else:
            ok, result = False, "用户拒绝了这个操作。不要再尝试，告诉用户没有执行"
        yield event("tool_end", tool=p["name"], ok=ok, result=result[:80])
        task.steps = [*task.steps, {"type": "tool", "name": p["name"], "ok": ok, "confirmed": approve}]
        task.messages = [*task.messages, {"role": "tool", "tool_call_id": p["id"], "content": result}]
        task.status, task.pending = "running", None
        s.commit()
    yield from drive(task_id)
