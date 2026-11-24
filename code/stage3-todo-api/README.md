# stage3-todo-api

Python 学习笔记「阶段三：FastAPI 后端开发」做到 3.20 节结束时的完整 todo 后端：注册登录（JWT）、每人只看自己的任务、分页、统一响应格式 `{code, msg, data}`、Alembic 迁移、CORS、请求日志、可部署到 Vercel；3.17 拆出 service 层，3.18 管理员角色（`/admin/users`），3.19 文件上传（`/files`），3.20 Redis（登录失败限制、管理员接口缓存）。

## 1. 建虚拟环境、装依赖

```bash
cd code/stage3-todo-api
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python -r requirements-dev.txt
```

- `requirements.txt`：线上运行要的依赖（Vercel 按它装）。
- `requirements-dev.txt`：再加上本地用的 uvicorn、pytest、httpx、alembic。

## 2. 建库

本机 brew 装的 Postgres，本地连接不用密码（`pg_isready` 看是否在运行）：

```bash
createdb stage3_todo         # 接口用的库
createdb stage3_todo_test    # 测试专用的库：每个测试都会清空它
```

## 2.5 装 Redis（3.20 起要用）

```bash
brew install redis
brew services start redis    # 或者临时运行：redis-server
redis-cli ping               # PONG
```

开发用 0 号库，测试用 15 号库（每个测试前清空）。

## 3. 配置 .env

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"   # 生成的随机串填到 .env 的 JWT_SECRET
```

| 变量 | 说明 | 默认 |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://localhost:5432/stage3_todo` | `.../todo` |
| `DEBUG` | `true` 时打印每条 SQL | `false` |
| `JWT_SECRET` | 签 token 的密钥 | `dev-secret-change-me`（`VERCEL=1` 时用它会启动失败） |
| `TOKEN_DAYS` | token 几天过期 | `7` |
| `CORS_ORIGINS` | 允许跨域的前端网址，JSON 格式 | `["http://localhost:5173"]` |
| `UPLOAD_DIR` | 上传文件存放的文件夹 | `uploads` |
| `REDIS_URL` | Redis 地址 | `redis://localhost:6379/0` |

`.env` 不提交（已写进 `.gitignore`）。

## 4. 跑迁移（建表）

```bash
.venv/bin/alembic upgrade head      # 按 migrations/versions/ 里的脚本建 users、tasks 表
.venv/bin/alembic current           # 看当前版本
```

以后改了 `app/models.py`：`.venv/bin/alembic revision --autogenerate -m "说明"` → 打开脚本检查 → `.venv/bin/alembic upgrade head`。

## 5. 启动

```bash
.venv/bin/uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs ：先 `POST /auth/register` 拿到 token，点右上角 **Authorize** 填进去，再试 `/tasks` 下的接口。

| 方法 | 路径 | 作用 | 要登录 |
|---|---|---|---|
| GET | `/` | 健康检查 | 否 |
| POST | `/auth/register` | 注册，直接返回 token | 否 |
| POST | `/auth/login` | 登录，返回 token | 否 |
| GET | `/auth/me` | 当前用户 | 是 |
| GET | `/tasks?done=false&page=1&size=20` | 自己的任务列表，分页 | 是 |
| POST | `/tasks` | 新建；自己有同名未完成任务则 409 | 是 |
| GET | `/tasks/{id}` | 详情；不存在或不是自己的都 404 | 是 |
| PATCH | `/tasks/{id}/done` | 标记完成 | 是 |
| DELETE | `/tasks/{id}` | 删除 | 是 |

## 6. 跑测试

```bash
.venv/bin/python -m pytest -q          # 测试连 stage3_todo_test，不碰 stage3_todo
.venv/bin/python -m pytest -q -k 404   # 只跑名字里带 404 的
```

## 文件对应笔记哪一节

| 文件 | 笔记 |
|---|---|
| `app/__init__.py`、`tests/__init__.py` | 3.1 项目准备（空文件） |
| `app/schemas.py` | 3.3 建；3.10 加 `TaskList`；3.13 加 `AuthIn`、`TokenOut`；3.14 `TaskList` 加 `page`、`size`；3.15 `TaskOut` 加 `priority` |
| `app/response.py` | 3.4 统一响应格式 `success` |
| `app/errors.py` | 3.5 错误处理（完整版，4 个处理器） |
| `app/db.py` | 3.7 建；3.9 加 `db_session`、`Db`；3.12 改读 `settings`；3.16 加 `NullPool` |
| `app/models.py` | 3.7 `Task`；3.13 `User`；3.14 `user_id` 外键和 `relationship`；3.15 `priority` |
| `app/config.py` | 3.12 建（pydantic-settings）；3.13 加 `jwt_secret`、`token_days`；3.16 加 `cors_origins`、`vercel`、`check_secret` |
| `app/routers/__init__.py` | 3.12（空文件） |
| `app/routers/tasks.py` | 3.12 从 main.py 拆出；3.14 整个换成「只看自己的 + 分页」版 |
| `app/security.py` | 3.13 密码哈希、JWT、`CurrentUser` |
| `app/routers/auth.py` | 3.13 注册、登录、`/auth/me` |
| `app/main.py` | 3.16 完整版（3.15 去掉 lifespan / create_all；3.16 加 CORS、日志中间件、健康检查） |
| `alembic.ini`、`migrations/` | 3.15（`alembic init migrations` 生成，`env.py` 按笔记改两处） |
| `migrations/versions/*_create_users_and_tasks.py` | 3.15 第一次迁移（按最终模型生成，已含 `priority` 列） |
| `index.py` | 3.16 Vercel 入口 |
| `requirements.txt` | 3.16 部署依赖 |
| `.env.example`、`.gitignore` | 3.7 建；3.12 加 `DEBUG`；3.13 加 `JWT_SECRET` |
| `tests/conftest.py` | 3.11 的「准备」和 `client` fixture 搬到这里，另加 `login` 帮手和 `auth` fixture |
| `tests/test_tasks.py` | 3.11 的五个测试（带上 `headers=auth`）+ 3.14 的隔离、分页测试 |
| `tests/test_auth.py` | 补充：3.13 注册登录 |
| `tests/test_app.py` | 补充：3.16 健康检查、CORS 预检；3.5 404 / 405 格式 |

3.2 的 `app/hello.py`、3.4～3.5 的 `api_demo.py`、3.8～3.9 的 `crud_demo.py` 是中途演示文件，没有放进来。
