# stage6-agent-demo：阶段六「Agent 开发」练习代码

一个「个人助手」Agent：查天气（假数据）、算数、发邮件（假的，只打印）。

## 准备

```bash
cd code/stage6-agent-demo
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install openai pydantic fastapi uvicorn langchain-openai langgraph langgraph-checkpoint-sqlite mcp jieba rank-bm25 pypdf
```

## 文件和小节

| 小节 | 文件 | 运行 |
|---|---|---|
| 公共 | `llm.py` 和阶段四一样；`tools.py` 三个工具和描述 | — |
| 6.1 最小循环 | `agent_min.py` | `python agent_min.py` |
| 6.2 校验、出错、人工确认 | `agent.py`（问到发邮件时输入 y 或 n） | `python agent.py` |
| 6.3 Trace | `trace_demo.py`，会在当前目录追加写 `traces.jsonl` | `python trace_demo.py` |
| 6.4 上下文和记忆 | `memory_demo.py` 裁剪和摘要；`memory_long.py` 长期记忆（写 `memory.json`） | `python memory_demo.py` |
| 6.5 LangChain | `lc_llm.py` 模型对象；`lc_demo.py` 模板、链、结构化输出 | `python lc_demo.py` |
| 6.6 LangGraph | `lg_agent.py` 图、Checkpoint、interrupt 人工确认 | `python lg_agent.py` |
| 6.7 MCP | `weather_server.py` 服务；`mcp_client.py` 客户端（会自己启动服务） | `python mcp_client.py` |
| 6.8 Skill | `skill_demo.py`，说明文件在 `skills/` | `python skill_demo.py` |
| 6.9 Agent 评测 | `eval_agent.py` 三版 system 对比 | `python eval_agent.py` |
| 6.10 多 Agent | `multi_agent.py` 文案 + 审核 | `python multi_agent.py` |
| 6.11 Agent 前端 | `agent_api.py` SSE 推送每一步 | `uvicorn agent_api:app --port 8420` |
| 6.12 先规划再执行 | `plan_agent.py` | `python plan_agent.py` |
| 6.13 自我修正 | `reflect_agent.py`（用 `sandbox.py` 跑测试） | `python reflect_agent.py` |
| 6.14 权限和沙箱 | `perm_demo.py` 按角色给工具；`sandbox.py` 子进程跑代码 | `python perm_demo.py` |
| 6.15 Skill 体系 | `skill_system.py`，带版本的 Skill 在 `skill_lib/` | `python skill_system.py` |
| 6.16 LangChain 进阶 | `lc_memory_rag.py` 记忆 + RAG 链（借用 `../stage5-rag-demo` 的检索） | `python lc_memory_rag.py` |
| 6.17 LangGraph 完整版 | `lg_full.py`，状态存在 `checkpoints.db` | `python lg_full.py start`，再 `python lg_full.py resume` |
| 6.18 多 Agent | `multi_graph.py` Planner / Executor / Writer / Reviewer | `python multi_graph.py` |
| 6.19 故障分析 | `failure_demo.py` 报错含糊、工具结果太长 | `python failure_demo.py` |
