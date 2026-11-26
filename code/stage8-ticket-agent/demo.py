# demo.py：当一个「前端」：提三个问题，第三个会停下来等确认
import json
import sys

import httpx

api = httpx.Client(base_url="http://localhost:8600", timeout=120)


def stream(path: str, body: dict) -> int | None:
    """读 SSE，把事件一行行打出来；返回任务 id。"""
    task_id = None
    with api.stream("POST", path, json=body) as r:
        buf = ""
        for chunk in r.iter_text():
            buf += chunk
            *events, buf = buf.split("\n\n")
            for block in events:
                kind = block.split("\n")[0].removeprefix("event: ")
                data = json.loads(block.split("\n")[1].removeprefix("data: "))
                if kind == "task":
                    task_id = data["id"]
                elif kind != "thinking":
                    print(f"  [{kind}] {json.dumps(data, ensure_ascii=False)[:110]}")
    return task_id


for q in ["外卖晚到能退款吗？", "帮我查一下订单 B2001", "订单 A1024 的外卖晚了很久才到，帮我退款"]:
    print("问：", q)
    tid = stream("/tasks", {"user": "xiaolin", "question": q})
    if api.get(f"/tasks/{tid}").json()["status"] == "waiting_confirm":
        approve = (sys.argv[1:] or ["y"])[0] == "y"
        print(f"  （用户点了{'确认' if approve else '拒绝'}）")
        stream(f"/tasks/{tid}/confirm", {"approve": approve})
    t = api.get(f"/tasks/{tid}").json()
    llm = [s for s in t["steps"] if s["type"] == "llm"]
    print(f"  任务 {tid}：{t['status']}，调模型 {len(llm)} 次，{sum(s['tokens'] for s in llm)} token\n")
