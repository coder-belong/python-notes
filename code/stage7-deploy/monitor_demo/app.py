# app.py：上线后怎么知道服务好不好：① 结构化日志 ② 指标（给 Prometheus 采集）③ 出错多了就告警
import json
import logging
import random
import time
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


# ---------- ① 结构化日志：每行一个 JSON，方便日志平台按字段搜索、统计 ----------
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"level": record.levelname, "msg": record.getMessage(), **getattr(record, "extra", {})}, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
log = logging.getLogger("app")
log.addHandler(handler)
log.setLevel(logging.INFO)

# ---------- ② 指标：请求数（按接口、状态码分）和耗时分布 ----------
REQUESTS = Counter("http_requests_total", "请求数", ["path", "status"])
LATENCY = Histogram("http_request_seconds", "请求耗时（秒）", ["path"], buckets=[0.05, 0.1, 0.3, 1, 3])

# ---------- ③ 告警：最近 20 个请求里 5xx 超过 30% 就报警 ----------
recent: deque[bool] = deque(maxlen=20)
alerted = False


def alert(text: str) -> None:
    # 真实项目里发到飞书 / 钉钉 / 企业微信的机器人 webhook，或者交给 Prometheus 的 Alertmanager
    print(f"🚨 告警：{text}", flush=True)


app = FastAPI()


@app.middleware("http")                              # 中间件（3.16 节）：每个请求都经过这里
async def observe(request: Request, call_next):
    global alerted
    start = time.perf_counter()
    response = await call_next(request)
    cost = time.perf_counter() - start
    path = request.url.path
    if path != "/metrics":
        REQUESTS.labels(path, str(response.status_code)).inc()
        LATENCY.labels(path).observe(cost)
        log.info("request", extra={"extra": {"path": path, "status": response.status_code, "ms": round(cost * 1000)}})
        recent.append(response.status_code >= 500)
        rate = sum(recent) / len(recent)
        if len(recent) >= 10 and rate > 0.3 and not alerted:
            alerted = True                            # 只报一次，免得刷屏；恢复后再重置
            alert(f"最近 {len(recent)} 个请求有 {rate:.0%} 出错，最后一个是 {path}")
    return response


@app.get("/chat")
async def chat() -> dict:
    time.sleep(random.uniform(0.05, 0.4))            # 模拟调模型的耗时
    return {"answer": "ok"}


@app.get("/flaky")
async def flaky() -> PlainTextResponse:
    if random.random() < 0.6:                         # 模拟一个不稳定的接口：六成会失败
        return PlainTextResponse("模型接口超时", status_code=502)
    return PlainTextResponse("ok")


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    """Prometheus 每隔几秒来拉一次这个接口，存成时间序列，Grafana 再画成图表。"""
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)
