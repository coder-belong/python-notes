# lc_memory_rag.py：LangChain 进阶：对话记忆 + 用链搭 RAG
import sys

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from lc_llm import llm

sys.path.insert(0, "../stage5-rag-demo")    # 借用阶段五写好的文档切分和 BM25 检索
from load_docs import load_chunks           # noqa: E402
from search import Searcher                 # noqa: E402

# ---------- ① 对话记忆：现在推荐用 LangGraph 的 Checkpoint，按 thread_id 各存各的 ----------
def reply(state: MessagesState) -> dict:
    system = ("system", "你是生活助手，回答一句话。")
    return {"messages": [llm.invoke([system, *state["messages"]])]}   # state 里是这个会话的全部历史


graph = StateGraph(MessagesState)
graph.add_node("reply", reply)
graph.add_edge(START, "reply")
chat = graph.compile(checkpointer=InMemorySaver())   # 每轮结束自动把消息存起来；真实项目换成存数据库的

for tid, q in [("a", "我叫小林"), ("a", "我叫什么？"), ("b", "我叫什么？")]:
    config = {"configurable": {"thread_id": tid}}     # 同一个 thread_id 就是同一个会话
    result = chat.invoke({"messages": [("user", q)]}, config)
    print(f"会话 {tid}：{q} → {result['messages'][-1].content}")
print("会话 a 存了几条：", len(chat.get_state({"configurable": {"thread_id": "a"}}).values["messages"]))

# ---------- ② RAG 链：检索 → 拼资料 → 回答 ----------
searcher = Searcher(load_chunks("../stage5-rag-demo/docs"))


def retrieve(question: str) -> str:
    hits = searcher.search(question, k=2)
    return "\n".join(f"[{c.source} · {c.title}] {c.text}" for _, c in hits) or "（没有找到相关资料）"


rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是豆豆咖啡的客服，只根据 <docs> 回答，一句话，末尾用括号标出处。\n<docs>\n{docs}\n</docs>"),
    ("user", "{question}"),
])
rag_chain = (
    {"docs": RunnableLambda(retrieve), "question": RunnablePassthrough()}   # 同一个问题分两路：一路去检索，一路原样传下去
    | rag_prompt
    | llm
    | StrOutputParser()
)
print(rag_chain.invoke("积分多久过期？"))
for piece in rag_chain.stream("外卖晚了能退款吗"):   # 整条链也能流式：最后一步的模型一边生成一边吐
    print(piece, end="|", flush=True)
print()
