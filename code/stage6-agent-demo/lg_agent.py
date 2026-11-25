# lg_agent.py：用 LangGraph 实现 6.2 节的 Agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

import tools as t
from lc_llm import llm


@tool   # 加上 @tool：函数名、参数类型、文档字符串自动变成 4.5 节那种工具描述
def get_weather(city: str) -> dict:
    """查某个城市明天的天气，返回天气、最高和最低气温（摄氏度）"""
    return t.get_weather(city)


@tool
def calculate(expression: str) -> float:
    """计算一个数学表达式，比如 (13-6)*2"""
    return t.calculate(expression)


@tool
def send_email(to: str, content: str) -> str:
    """给某人发邮件"""
    answer = interrupt({"action": "send_email", "to": to})   # 暂停整张图，等用户回复；恢复时拿到用户的回答
    if answer != "y":
        return "用户拒绝了这个操作。不要再尝试，直接告诉用户没有执行"
    return t.send_email(to, content)


TOOLS = [get_weather, calculate, send_email]
model = llm.bind_tools(TOOLS)   # 把工具描述带上，相当于 4.5 节的 tools=TOOLS


def agent(state: MessagesState) -> dict:
    """节点：调一次模型。返回的消息会追加进 state["messages"]。"""
    system = ("system", "你是个人助手，可以调用工具完成任务。需要数字计算时用 calculate，不要自己心算。")
    return {"messages": [model.invoke([system, *state["messages"]])]}


graph = StateGraph(MessagesState)                    # State：图里流转的数据，这里就是消息列表
graph.add_node("agent", agent)                       # Node：一个步骤
graph.add_node("tools", ToolNode(TOOLS))             # 现成的节点：执行模型要调的工具，结果放回消息
graph.add_edge(START, "agent")                       # Edge：先走 agent
graph.add_conditional_edges("agent", tools_condition)   # 模型要调工具 → tools；不调 → 结束
graph.add_edge("tools", "agent")                     # 工具执行完回到 agent，就是 6.1 节的循环
app = graph.compile(checkpointer=InMemorySaver())    # Checkpoint：每一步的状态都存下来，暂停后能接着跑

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo-1"}, "recursion_limit": 20}   # thread_id：哪一次对话；recursion_limit：最多走几步
    result = app.invoke({"messages": [("user", "明天北京和上海的最高气温差几度？发邮件告诉小王。")]}, config)

    for m in result["messages"]:   # 看看图里都走了哪些步
        if m.type == "ai" and m.tool_calls:
            print("调工具：", [(c["name"], str(c["args"])[:40]) for c in m.tool_calls])   # 参数只显示前 40 个字
        elif m.type == "tool":
            print("结果：  ", m.content[:50])

    if "__interrupt__" in result:   # 停在 send_email 里等确认
        print("暂停，等确认：", result["__interrupt__"][0].value)
        result = app.invoke(Command(resume="y"), config)   # 用户点了确认：同一个 thread_id 接着跑
    print(result["messages"][-1].content)
