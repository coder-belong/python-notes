# lg_full.py：LangGraph 完整版：3 个工具 + 失败重试 + 断点恢复 + Trace 和每步成本 + 流式输出
import sqlite3
import sys

from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, RetryPolicy

from lc_llm import llm
from lg_agent import calculate, send_email   # 6.6 节写好的两个工具（send_email 里有 interrupt 等确认）
import tools as t

PRICE = {"hit": 0.006, "miss": 0.3, "output": 1.2}   # 美元 / 百万 token，和 4.3 节一样
failed: set[str] = set()


@tool
def get_weather(city: str) -> dict:
    """查某个城市明天的天气，返回天气、最高和最低气温（摄氏度）"""
    if city not in failed:          # 模拟不稳定的天气接口：每个城市第一次查都超时
        failed.add(city)
        raise TimeoutError(f"天气接口超时（{city}），请重试")
    return t.get_weather(city)


TOOLS = [get_weather, calculate, send_email]
model = llm.bind_tools(TOOLS)


def agent(state: MessagesState) -> dict:
    system = ("system", "你是个人助手，可以调用工具完成任务。工具报错可以重试一次。需要数字计算时用 calculate。")
    return {"messages": [model.invoke([system, *state["messages"]])]}


graph = StateGraph(MessagesState)
graph.add_node("agent", agent, retry_policy=RetryPolicy(max_attempts=3))   # 调模型这一步抛异常（网络、限流）自动重试 3 次
graph.add_node("tools", ToolNode(TOOLS, handle_tool_errors=True))   # 工具抛异常不崩：把报错变成一条 tool 消息交给模型
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

conn = sqlite3.connect("checkpoints.db", check_same_thread=False)   # Checkpoint 存进 SQLite 文件：进程退出了也还在
app = graph.compile(checkpointer=SqliteSaver(conn))
config = {"configurable": {"thread_id": "task-42"}, "recursion_limit": 20}


def cost(msg) -> float:
    u = msg.response_metadata["token_usage"]
    return (u["prompt_cache_hit_tokens"] * PRICE["hit"] + u["prompt_cache_miss_tokens"] * PRICE["miss"]
            + u["completion_tokens"] * PRICE["output"]) / 1_000_000


def run(inp) -> None:
    total = 0.0
    # stream_mode="updates"：每个节点一跑完就吐出它这一步的结果，前端可以边跑边显示（Trace 也从这里记）
    for update in app.stream(inp, config, stream_mode="updates"):
        for node, data in update.items():
            if node == "__interrupt__":
                print(f"  ⏸ 暂停等确认：{data[0].value}")
                continue
            for m in data["messages"]:
                if node == "agent":
                    total += cost(m)
                    calls = [f"{c['name']}({c['args']})"[:40] for c in m.tool_calls]
                    print(f"  [agent] {m.usage_metadata['total_tokens']} token ${cost(m):.6f}  "
                          + (f"要调：{calls}" if calls else f"回答：{m.content[:40]!r}"))
                else:
                    print(f"  [tools] {m.name} → {m.content[:50].replace(chr(10), ' ')}")
    print(f"  本次合计 ${total:.6f}")


if __name__ == "__main__":
    if sys.argv[1:] == ["start"]:
        run({"messages": [("user", "明天北京和上海的最高气温差几度？发邮件告诉小王。")]})
    elif sys.argv[1:] == ["resume"]:   # 另开一个进程：从 SQLite 里读出 task-42 停在哪，接着跑
        print("  停在：", app.get_state(config).next)
        run(Command(resume="y"))
