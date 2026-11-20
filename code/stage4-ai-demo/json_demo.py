# json_demo.py
from typing import Literal

import openai
from pydantic import BaseModel, Field, ValidationError

from llm import MODEL, NO_THINKING, client


class TaskDraft(BaseModel):                       # 想要的格式，和 3.3 节写请求体一样
    title: str = Field(max_length=50)
    priority: Literal["high", "medium", "low"]    # 只能是这三个之一
    due: str | None                               # 截止日期，没有就是 None


# system 里写清楚：① 必须出现 json 这个词 ② 给一个格式示例
SYSTEM = """从用户的话里提取一个待办任务，只输出 json，格式：
{"title": "任务标题", "priority": "high / medium / low 三选一", "due": "截止日期 YYYY-MM-DD，没说就是 null"}"""


def extract(text: str) -> TaskDraft:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        response_format={"type": "json_object"},  # JSON 模式：保证输出是合法的 JSON
        max_tokens=200,                           # 留够长度，被截断的 JSON 解析不了
        extra_body=NO_THINKING,
    )
    content = resp.choices[0].message.content
    print(content)                                # 模型输出的 JSON 字符串
    return TaskDraft.model_validate_json(content) # 解析 + 校验，不合格就抛 ValidationError


task = extract("下周五之前一定要把季度报告交了，今天是 2026-11-20")
# {"title": "提交季度报告", "priority": "high", "due": "2026-11-27"}
print(task)            # title='提交季度报告' priority='high' due='2026-11-27'
print(task.priority)   # high                     已经是 TaskDraft 对象，直接用点号取


try:
    client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": "提取任务：明天交报告"}],   # prompt 里没有 json
        response_format={"type": "json_object"}, extra_body=NO_THINKING,
    )
except openai.BadRequestError as e:
    print(e.message)
# Error code: 400 - Prompt must contain the word 'json' in some form to use 'response_format' of type 'json_object'. (request_id: ...)


try:
    TaskDraft.model_validate_json('{"title": "交报告", "priority": "urgent", "due": null}')   # 假设模型输出了 urgent
except ValidationError as e:
    print(e.errors()[0]["msg"])   # Input should be 'high', 'medium' or 'low'
