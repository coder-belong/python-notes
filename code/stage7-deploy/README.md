# stage7-deploy：阶段七「部署与工程化」练习代码

| 小节 | 文件 | 运行 |
|---|---|---|
| 7.1～7.3 | `Dockerfile`（构建阶段三的后端）、`docker-compose.yml`（后端 + PostgreSQL + Redis + Nginx）、`nginx.conf` | 先 `colima start`，再 `docker-compose up -d --build`，打开 https://localhost:8443 |
| 7.4 任务队列 | `queue_demo/`：`worker.py`、`app.py`、`client_demo.py`（ARQ + Redis） | 见笔记 7.4 节 |
| 7.5 监控 | `monitor_demo/app.py`（JSON 日志、Prometheus 指标、告警）、`load_demo.py` | `cd monitor_demo && ../.venv/bin/uvicorn app:app --port 8900`，再跑 `load_demo.py` |
| 7.6 CI | `ci/stage3-tests.yml`（GitHub Actions）、`ci/docker-compose.ci.yml`（本机模拟） | `cd ci && docker-compose -f docker-compose.ci.yml up --abort-on-container-exit --exit-code-from tests` |

准备：

```bash
brew install colima docker docker-compose
cp .env.example .env               # 改成自己的随机密码、密钥
mkdir -p certs && openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj "/CN=localhost" -keyout certs/local.key -out certs/local.crt
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install arq fastapi uvicorn httpx prometheus-client
```
