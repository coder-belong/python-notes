# reflect_agent.py：自我修正：写代码 → 跑测试 → 把报错交回给模型 → 改，最多 3 轮
import re

from llm import MODEL, NO_THINKING, client
from sandbox import run_code

TASK = """写一个 Python 函数 parse_price(text: str) -> float，把各种写法的价格转成数字：
'¥1,299.50' → 1299.5，'12元' → 12.0，'$ 8' → 8.0，'免费' → 0.0，'3.5万' → 35000.0"""

TESTS = """
cases = [('¥1,299.50', 1299.5), ('12元', 12.0), ('$ 8', 8.0), ('免费', 0.0),
         ('3.5万', 35000.0), ('1.2k', 1200.0), ('約 ¥980', 980.0)]
wrong = []
for text, want in cases:
    try:
        got = parse_price(text)
    except Exception as e:
        got = f'{type(e).__name__}: {e}'
    if got != want:
        wrong.append(f'parse_price({text!r}) 应该是 {want}，实际是 {got!r}')
if wrong:
    raise SystemExit('\\n'.join(wrong))   # 说清楚哪条错了、差在哪，模型才知道怎么改
print('全部通过')
"""   # 最后两条是任务里没写的情况：看模型能不能根据报错补上


def extract_code(text: str) -> str:
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)   # 取出 ```python 代码块里的内容
    return m.group(1) if m else text


messages = [
    {"role": "system", "content": "你是 Python 程序员，只输出一个 ```python 代码块，不要解释。"},
    {"role": "user", "content": TASK},
]
for round in range(1, 4):
    reply = client.chat.completions.create(model=MODEL, messages=messages, extra_body=NO_THINKING).choices[0].message.content
    code = extract_code(reply)
    ok, output = run_code(code + TESTS)           # 在沙箱里跑：模型写的代码 + 测试
    print(f"第 {round} 轮：{'通过' if ok else '失败'}  {output.splitlines()[-1]}")
    if ok:
        break
    # 反思：把代码和报错原样交回去，让模型自己找原因、改
    messages += [
        {"role": "assistant", "content": reply},
        {"role": "user", "content": f"测试没通过，输出：\n{output}\n\n先想清楚是哪种输入没处理好，再给出完整的新代码。"},
    ]
