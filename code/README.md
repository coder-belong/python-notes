# 笔记配套代码

`content/notes.md` 每个阶段的示例代码，整理成能直接运行的工程。每个目录里的 `README.md` 写了怎么建环境、哪个文件对应哪一节。

| 目录 | 内容 |
|---|---|
| `stage1-python-basics/` | 阶段一：Python 语言基础，每节一个子目录 |
| `stage2-advanced/` | 阶段二：Python 进阶与工程化，每节一个子目录 |
| `stage3-todo-api/` | 阶段三：3.16 节结束时的完整 todo 后端（FastAPI + Postgres + Alembic + JWT），带测试 |
| `stage4-ai-demo/` | 阶段四：大模型应用基础（DeepSeek + openai SDK），4.1～4.11 |
| `stage5-rag-demo/` | 阶段五：RAG 与知识库（关键词检索版，不需要向量模型），5.1～5.5 |
| `stage6-agent-demo/` | 阶段六：Agent 开发（手写 Agent、LangChain、LangGraph、MCP、Skill），6.1～6.11 |

- 每个工程各自建虚拟环境 `.venv`，不提交；换电脑后按 README 重建。
- `stage3-todo-api/.env` 放本机的数据库地址和密钥，不提交；照着 `.env.example` 自己建。
- `stage4-ai-demo`、`stage5-rag-demo`、`stage6-agent-demo` 要先设好环境变量 `DEEPSEEK_API_KEY`。
