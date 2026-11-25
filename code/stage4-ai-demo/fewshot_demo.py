# fewshot_demo.py
from llm import MODEL, NO_THINKING, client

COMMENTS = [
    "外卖送得很快，还是热的，好评！",
    "等了一个半小时，饭都凉了。",
    "味道还行吧，就是分量有点少。",
    "建议加个备注功能，我想写不要香菜。",
    "客服态度很好，帮我退了款。",
]

# 写法一：只说要求（zero-shot：一个示例都不给）
ZERO = "判断这条外卖评论的类型：好评、差评、建议。"


def classify_zero(text: str) -> str:
    resp = client.chat.completions.create(   # 发一次请求：system 写要求，user 放评论
        model=MODEL,
        messages=[{"role": "system", "content": ZERO}, {"role": "user", "content": text}],
        extra_body=NO_THINKING,
    )
    return resp.choices[0].message.content

# 写法二：规则写清楚 + 给几个示例（few-shot）
FEW = """判断外卖评论的类型，只输出一个词：好评、差评、建议。
- 有抱怨就算差评，哪怕语气很客气
- 提了具体改进想法才算建议"""

EXAMPLES = [   # 示例写成一问一答的历史消息：模型会照着前面「自己」的回答格式来
    {"role": "user", "content": "包装很用心，下次还点。"},
    {"role": "assistant", "content": "好评"},
    {"role": "user", "content": "还可以，就是有点咸。"},
    {"role": "assistant", "content": "差评"},
    {"role": "user", "content": "希望能出个小份的套餐。"},
    {"role": "assistant", "content": "建议"},
]


def classify_few(text: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        # 顺序：system → 示例 → 这次真正要判断的评论
        messages=[{"role": "system", "content": FEW}, *EXAMPLES, {"role": "user", "content": text}],
        max_tokens=5,   # 只要一个词，限短一点，模型想多说也说不了
        extra_body=NO_THINKING,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":   # 直接运行这个文件才执行；4.9 节 import 它的时候不执行
    for c in COMMENTS:
        # repr：把换行显示成 \n，看清楚模型到底输出了什么
        print(repr(classify_zero(c)).ljust(12), repr(classify_few(c)))
