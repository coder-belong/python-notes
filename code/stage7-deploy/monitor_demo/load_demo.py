# load_demo.py：打一些请求，然后看指标
import random

import httpx

api = httpx.Client(base_url="http://localhost:8900")
random.seed(7)
for _ in range(30):
    api.get(random.choice(["/chat", "/chat", "/flaky"]))
print("--- 第一轮：正常流量（大部分是 /chat）打完")
for _ in range(15):
    api.get("/flaky")                                  # 第二轮：模型接口出问题，连续调不稳定的接口
print("--- 第二轮：连续调 /flaky 打完")
lines = [line for line in api.get("/metrics").text.splitlines() if line.startswith(("http_requests_total{", "http_request_seconds_count", "http_request_seconds_bucket{le=\"0.3\""))]
print("\n".join(lines))
