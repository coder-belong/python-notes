# lc_demo.py
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from lc_llm import llm

# ① 最简单的调用：返回的是消息对象，文字在 .content
print(llm.invoke("用一句话介绍 LangChain").content)

# ② Prompt 模板：{占位符} 调用时再填
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，回答一句话。"),
    ("user", "{question}"),
])
chain = prompt | llm | StrOutputParser()   # | 把几步串成一条链：填模板 → 调模型 → 取出文字
print(chain.invoke({"role": "健身教练", "question": "每天走多少步合适？"}))


# ③ 结构化输出：直接拿到 Pydantic 对象（4.4 节要自己写的校验，它包好了）
class Task(BaseModel):
    title: str
    due: str | None


extract = llm.with_structured_output(Task, method="function_calling")
print(extract.invoke("下周五前交季度报告，今天是 2026-11-25"))
