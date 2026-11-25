# multi_agent.py：两个角色分工：写的人只管写，审的人只管挑毛病，最多改 3 轮
from llm import MODEL, NO_THINKING, client


def chat(system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        extra_body=NO_THINKING,
    )
    return resp.choices[0].message.content


WRITER = "你是文案，给奶茶店新品写朋友圈文案。按要求修改时，只输出改好的文案。"
REVIEWER = """你是审核，检查朋友圈文案是否满足：
1. 写出了价格  2. 不用「最」「第一」这类绝对化用语（广告法）
全部满足只输出「通过」；否则逐条列出问题，不要自己改写。"""


def review(draft: str) -> str:
    problems = []
    if len(draft) > 40:   # 数字数这种事交给代码：模型数不准
        problems.append(f"超过 40 字（现在 {len(draft)} 字），要删减")
    result = chat(REVIEWER, draft)
    if not result.strip().startswith("通过"):
        problems.append(result)
    return "\n".join(problems) or "通过"   # 没有问题时 join 出空字符串，or 换成「通过」

task = "新品：桂花酒酿奶茶，18 元，秋季限定。"
draft = chat(WRITER, task)
for round in range(1, 4):
    print(f"第 {round} 稿（{len(draft)} 字）：{draft}")
    opinion = review(draft)
    print(f"审核：{opinion}\n")
    if opinion == "通过":
        break
    draft = chat(WRITER, f"{task}\n上一稿：{draft}\n审核意见：{opinion}\n按意见修改。")
