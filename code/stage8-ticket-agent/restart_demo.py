# restart_demo.py：任务停在「等确认」时服务重启了，用户确认后还能接着跑吗？
import json
import subprocess
import time

import httpx

api = httpx.Client(base_url="http://localhost:8600", timeout=120)


def start_server() -> subprocess.Popen:
    p = subprocess.Popen([".venv/bin/uvicorn", "api:app", "--port", "8600"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            api.get("/docs")
            return p
        except httpx.ConnectError:
            time.sleep(0.5)
    raise RuntimeError("服务没起来")


def events(path: str, body: dict) -> list[tuple[str, dict]]:
    out, buf = [], ""
    with api.stream("POST", path, json=body) as r:
        for chunk in r.iter_text():
            buf += chunk
            *blocks, buf = buf.split("\n\n")
            out += [(b.split("\n")[0][7:], json.loads(b.split("\n")[1][6:])) for b in blocks]
    return out


server = start_server()
ev = events("/tasks", {"user": "xiaolin", "question": "订单 A1025 晚到了，帮我退款"})
print("A1025：", [k for k, _ in ev], "→", ev[-1][1].get("text", "")[:70])

ev = events("/tasks", {"user": "xiaolin", "question": "订单 A1024 晚到了 40 多分钟，帮我退款"})
task_id = next(d["id"] for k, d in ev if k == "task")
print("A1024：停在", ev[-1][0], ev[-1][1].get("tool"))

server.terminate()
server.wait()
print("……服务重启……")
server = start_server()
print("重启后查任务：", api.get(f"/tasks/{task_id}").json()["status"])
ev = events(f"/tasks/{task_id}/confirm", {"approve": True})
print("确认后：", [k for k, _ in ev], "→", ev[-1][1].get("text", "")[:60])
server.terminate()
