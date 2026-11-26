# stage4-ai-demo：阶段四「大模型应用基础」练习代码

调大模型的练习：DeepSeek 模型，`openai` SDK。每个文件都能单独运行。

## 准备

```bash
echo ${#DEEPSEEK_API_KEY}      # 先确认 key 设好了：输出三十几的数字就对了
cd code/stage4-ai-demo           # 在 python-notes 仓库根目录下执行
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install openai pydantic fastapi uvicorn
```

## 文件和小节

| 小节 | 文件 | 运行 |
|---|---|---|
| 公共 | `llm.py`：client、模型名、关思考的参数，其他文件都 import 它 | — |
| 4.1 第一次调用 | `hello_llm.py` 最小调用；`think.py` 思考模式 | `python hello_llm.py` |
| 4.2 消息和 Token | `sys_demo.py` System Prompt；`history_demo.py` 多轮对话；`token_demo.py` 数 token、max_tokens 截断 | `python sys_demo.py` |
| 4.3 成本、超时、限流 | `cost_demo.py` 算钱和缓存；`error_demo.py` 超时和常见错误；`limit_demo.py` 用 Semaphore 控制并发 | `python cost_demo.py` |
| 4.4 Structured Output | `json_demo.py` JSON 模式 + Pydantic 校验 | `python json_demo.py` |
| 4.5 Function Calling | `tool_demo.py` 模型调用查任务、完成任务两个函数 | `python tool_demo.py` |
| 4.6 流式和 SSE | `stream_demo.py` 流式输出；`chat_api_min.py` SSE 最小版；`chat_api.py` FastAPI SSE 完整版（断开、出错、保存）；`chat.mjs` 前端接收和取消 | 见下面 |
| 4.7 生成原理 | `next_token_demo.py` 看每一步的候选 token 和概率 | `python next_token_demo.py` |
| 4.8 Prompt 和 Few-shot | `fewshot_demo.py` 只写要求 vs 加规则和示例 | `python fewshot_demo.py` |
| 4.9 效果评估 | `eval_demo.py` 12 条评测集，对比两种写法 | `python eval_demo.py` |
| 4.10 换模型 | `models_demo.py` 配置化切换厂商和模型 | `python models_demo.py` |
| 4.11 Prompt 注入 | `inject_demo.py` 注入演示、加标签防护、敏感信息打码 | `python inject_demo.py` |
| 4.12 前端流式渲染 | `chat_web.py` 多轮流式接口；`web/index.html` 聊天页（Markdown 渲染、停止、重试、多会话） | `uvicorn chat_web:app --port 8430`，浏览器打开 http://localhost:8430 |

4.6 要开两个终端：

```bash
uvicorn chat_api:app --port 8410     # 终端 1：启动后端
```

```bash
node chat.mjs                        # 终端 2：前端读流，第二段 2 秒后取消
```

模型每次的回答都会有点不一样，笔记里注释的输出是其中一次实际运行的结果。

## 4.13～4.14：本地模型、看图、听语音

| 小节 | 文件 | 运行 |
|---|---|---|
| 4.13 本地模型 | `local_demo.py` 用 Ollama 跑通义千问 1.5B，和 DeepSeek 比 4.9 节的评测集 | 先 `ollama serve`，再 `python local_demo.py` |
| 4.14 看图 | `vision_demo.py` 读小票转 JSON（默认 DeepSeek，加 `local` 用本地 Qwen2.5-VL 3B）；`make_receipt.py` 画小票图片 | `python vision_demo.py` |
| 4.14 听语音 | `speech_demo.py` Whisper 识别语音，再整理成 JSON | `HF_ENDPOINT=https://hf-mirror.com python speech_demo.py` |

额外的依赖：`uv pip install pillow faster-whisper`。Ollama 的模型从魔搭下载：

```bash
ollama pull modelscope.cn/Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M
ollama pull modelscope.cn/ggml-org/Qwen2.5-VL-3B-Instruct-GGUF:Q4_K_M
```
