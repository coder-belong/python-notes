# 阶段二：Python 进阶与工程化（示例代码）

代码来自 `python-notes/content/notes.md` 的「阶段二」，每节一个目录。

## 建环境

```bash
cd code/stage2-advanced
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python httpx fastapi uvicorn ruff
```

- `httpx`：2.6 的所有例子
- `fastapi`、`uvicorn`：2.8 的 `lifespan.py`
- `ruff`：2.2 演示格式化和检查

**运行方式**：先 `cd` 进对应小节目录，再用 `../.venv/bin/python 文件名` 运行。也可以先 `source .venv/bin/activate`，之后直接 `python 文件名`。

## 文件一览

| 小节 | 文件 | 说明 | 运行命令 |
|---|---|---|---|
| 2.1 类型注解 | `2.1-type-hints/type_hints.py` | 基本类型、容器、`\|` / None、Literal、Callable、自定义类当类型、注解不在运行时检查 | `cd 2.1-type-hints && ../.venv/bin/python type_hints.py` |
| 2.2 uv / pyproject / Ruff | `2.2-tooling/ruff_before.py` | 格式化前的代码，用来演示 ruff（直接运行无输出） | `cd 2.2-tooling && ../.venv/bin/ruff check ruff_before.py && ../.venv/bin/ruff format --diff ruff_before.py` |
| | `2.2-tooling/ruff_after.py` | `ruff format` 之后的样子 | `cd 2.2-tooling && ../.venv/bin/python ruff_after.py` |
| 2.3 日志、环境变量、时间 | `2.3-logging-env-time/logging_env_time.py` | logging 配置和级别、`os.environ.get`、UTC 时间 | `cd 2.3-logging-env-time && ../.venv/bin/python logging_env_time.py`（试试 `DATABASE_URL=xxx ../.venv/bin/python logging_env_time.py`） |
| 2.4 调试 | `2.4-debugging/debug_demo.py` | **故意报错**：看懂 traceback | `cd 2.4-debugging && ../.venv/bin/python debug_demo.py` |
| | `2.4-debugging/fstring_debug.py` | `f"{x=}"` 打印调试 | `cd 2.4-debugging && ../.venv/bin/python fstring_debug.py` |
| | `2.4-debugging/pdb_demo.py` | **交互式**：`breakpoint()` 进 pdb，按笔记输入 `p item`、`n`、`c` 等 | `cd 2.4-debugging && ../.venv/bin/python pdb_demo.py`；不想交互可以管道喂命令：`printf 'p item\np total\nn\np total\nc\np item, total\nc\n' \| ../.venv/bin/python pdb_demo.py` |
| 2.5 async / await | `2.5-async/sync_fetch.py` | 同步写法一个一个等，约 3 秒 | `cd 2.5-async && ../.venv/bin/python sync_fetch.py` |
| | `2.5-async/async_fetch.py` | `async`/`await`/`gather` 一起等，约 1 秒 | `cd 2.5-async && ../.venv/bin/python async_fetch.py` |
| | `2.5-async/forget_await.py` | **常见错误**：忘了 await，打印协程对象 + RuntimeWarning | `cd 2.5-async && ../.venv/bin/python forget_await.py` |
| | `2.5-async/await_in_def.py` | **故意报错**：普通 def 里写 await → SyntaxError | `cd 2.5-async && ../.venv/bin/python await_in_def.py` |
| | `2.5-async/timeout_demo.py` | `asyncio.timeout` 超时取消 | `cd 2.5-async && ../.venv/bin/python timeout_demo.py` |
| 2.6 httpx（需联网，访问 httpbin.org） | `2.6-httpx/get_demo.py` | GET + 查询参数 + 读 JSON | `cd 2.6-httpx && ../.venv/bin/python get_demo.py` |
| | `2.6-httpx/post_demo.py` | POST JSON + 请求头 | `cd 2.6-httpx && ../.venv/bin/python post_demo.py` |
| | `2.6-httpx/status_demo.py` | 404 不自动报错、`raise_for_status()` | `cd 2.6-httpx && ../.venv/bin/python status_demo.py` |
| | `2.6-httpx/timeout_demo.py` | 请求超时 `httpx.TimeoutException` | `cd 2.6-httpx && ../.venv/bin/python timeout_demo.py` |
| | `2.6-httpx/client_demo.py` | `httpx.Client` 复用连接 | `cd 2.6-httpx && ../.venv/bin/python client_demo.py` |
| | `2.6-httpx/async_client.py` | `AsyncClient` + `gather` 并发请求（约 6 秒） | `cd 2.6-httpx && ../.venv/bin/python async_client.py` |
| | `2.6-httpx/retry.py` | 5xx/429 重试 + 指数退避（约 7 秒） | `cd 2.6-httpx && ../.venv/bin/python retry.py` |
| 2.7 线程、进程、协程 | `2.7-concurrency/to_thread.py` | `asyncio.to_thread` 在 async 里跑同步慢函数 | `cd 2.7-concurrency && ../.venv/bin/python to_thread.py` |
| 2.8 with 和上下文管理器 | `2.8-context-manager/with_file.py` | with 和等价的 try/finally（会写出 `a.txt`，无输出） | `cd 2.8-context-manager && ../.venv/bin/python with_file.py` |
| | `2.8-context-manager/timer_cm.py` | `@contextmanager` 自己写计时器 | `cd 2.8-context-manager && ../.venv/bin/python timer_cm.py` |
| | `2.8-context-manager/lifespan.py` | FastAPI `lifespan`。直接运行只是定义 app、无输出；用 uvicorn 启动才能看到启动/关闭打印，Ctrl+C 停止 | `cd 2.8-context-manager && ../.venv/bin/uvicorn lifespan:app` |
