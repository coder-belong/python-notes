# client_demo.py：提交两个任务，每秒查一次进度
import time

import httpx

api = httpx.Client(base_url="http://localhost:8800")
ids = {t: api.post("/reports", json={"topic": t}).json()["job_id"] for t in ["季度销售", "会失败一次"]}
print("提交了：", {t: i[:8] for t, i in ids.items()}, "（接口马上就返回了）")

for _ in range(12):
    time.sleep(1)
    states = {t: api.get(f"/reports/{i}").json() for t, i in ids.items()}
    line = "  ".join(f"{t}: {s['status']} {s.get('progress', {}).get('step', '-')}/4" for t, s in states.items())
    print(line)
    if all(s["status"] == "complete" for s in states.values()):
        for t, s in states.items():
            print(f"  {t} → {s['result']}（试了 {s['tries']} 次）")
        break
