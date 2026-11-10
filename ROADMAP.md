# Python 技术成长路线

12 周，6 个阶段。勾上的是 `content/notes.md` 里已经写了的，后面括号注明在第几节；没勾的是待补充。

> 补内容前建议先改页面结构：按阶段拆成多个 md 文件、页面一次只显示一个阶段、侧栏按阶段折叠并显示进度。不然内容多了很难维护。

---

## 阶段一：Python 语言基础（第 1～2 周）

- [x] 基础语法、变量、数据类型（第 1 节）
- [x] 列表、元组、字典、集合（第 3、4 节）
- [x] 条件判断、循环、函数（第 2、5 节）
- [x] 模块、包、导入机制（第 6 节）
- [ ] 面向对象、继承、多态：类在第 7、8 节，**继承、多态还没写**
- [x] 异常处理、文件读写（第 9、10 节）
- [ ] 装饰器、生成器、迭代器：装饰器（第 5 节）、生成器（第 10 节）已写，**迭代器（`__iter__` / `__next__`、`iter()` / `next()`）还没写**

## 阶段二：Python 进阶与工程化（第 3～4 周）

- [ ] pip、uv、虚拟环境：第 0 节有 uv 和虚拟环境的基本用法，**可以补 pip 对比、常用命令**
- [ ] requirements.txt / pyproject.toml
- [x] 类型注解 Type Hints（第 1、5 节，散在各处）
- [x] Pydantic 数据校验（第 15 节）
- [ ] asyncio 异步编程：第 12 节有 async / await 基础，**可以补 `gather`、并发请求、超时**
- [x] 日志管理（第 11 节）
- [x] 单元测试 pytest（第 21 节）
- [ ] Git、代码规范（Ruff 只顺带提过）

## 阶段三：Python 后端开发（第 5～6 周）

- [ ] HTTP、RESTful API：状态码、方法、URL 设计
- [x] FastAPI（第 13、14 节）
- [x] 请求与响应（第 15、16 节）
- [x] 路由、依赖注入（第 19、20 节；APIRouter 拆文件在第 22 节练习题里）
- [ ] Middleware 中间件
- [ ] JWT 身份认证（含密码哈希）
- [x] SQLAlchemy ORM（第 17、18 节）
- [ ] MySQL / PostgreSQL：现在用 SQLite，**补换数据库的连接方式和 alembic 迁移实操**
- [ ] Redis：缓存、计数、过期时间

## 阶段四：AI 应用开发（第 7～8 周）

- [ ] LLM API 调用
- [ ] Prompt Engineering
- [ ] Structured Output（结合 Pydantic）
- [ ] Function Calling
- [ ] Streaming 流式输出
- [ ] Embedding 向量化
- [ ] RAG 检索增强生成
- [ ] 向量数据库

## 阶段五：Agent 开发（第 9～10 周）

- [ ] Agent 基本原理
- [ ] Tool Calling
- [ ] 工作流编排
- [ ] LangGraph
- [ ] 多 Agent 协作
- [ ] Memory 记忆机制
- [ ] Human-in-the-loop
- [ ] Agent 状态管理

## 阶段六：项目实战与部署（第 11～12 周）

- [ ] Docker
- [ ] Linux 部署
- [ ] Nginx
- [ ] Celery / 消息队列
- [ ] SSE / WebSocket（可以和阶段四的流式输出放一起讲）
- [ ] 任务队列
- [ ] 错误处理与监控
- [ ] CI/CD

---

## 写作约定（沿用现有笔记）

- 每个 `## 二级标题` 是一节，会出现在左侧目录，有「学完了」勾选和单独计时。
- 代码块写上语言（```python），每段代码都能直接复制运行，注释里写上输出。
- 只讲「会用 + 看懂别人代码」需要的程度，原理点到为止。
