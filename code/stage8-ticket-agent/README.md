# stage8-ticket-agent：阶段八综合项目「智能售后 Agent」

查规章（混合检索）、查订单、退款前人工确认、SSE 推送每一步、任务记录存 SQLite（服务重启能接着跑）、评测。借用了 `../stage5-rag-demo` 的检索代码。

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install openai fastapi uvicorn sqlalchemy pydantic httpx jieba rank-bm25 pypdf fastembed numpy
export HF_ENDPOINT=https://hf-mirror.com
uvicorn api:app --port 8600        # 终端 1
python demo.py                     # 终端 2：三个场景；python demo.py n 表示拒绝退款
python restart_demo.py             # 不符合规则、等确认时重启服务（自己会起服务，先关掉终端 1）
python eval_agent.py               # 评测：看数据库里有没有退款
```

| 文件 | 内容 |
|---|---|
| `db.py` | 订单、任务、退款三张表 |
| `tools.py` | search_kb / get_order / refund_order |
| `agent.py` | Agent 循环，每一步存库，高风险停下等确认 |
| `api.py` | POST /tasks、POST /tasks/{id}/confirm（SSE），GET /tasks/{id} |
| `frontend-review/` | 8.5 节的两个 JS 小例子：`node event_loop.mjs` |
