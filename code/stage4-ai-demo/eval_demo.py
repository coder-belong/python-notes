# eval_demo.py
from fewshot_demo import classify_few, classify_zero

# 评测集：输入 + 标准答案。平时攒下来的真实例子最好，尤其是以前答错过的
CASES = [
    ("送得很快，还是热的。", "好评"),
    ("等了一个半小时，饭都凉了。", "差评"),
    ("味道还行吧，就是分量有点少。", "差评"),
    ("建议加个备注功能，我想写不要香菜。", "建议"),
    ("客服态度很好，帮我退了款。", "好评"),
    ("骑手把汤洒了一半。", "差评"),
    ("能不能晚上也营业到十二点？", "建议"),
    ("一般般，没有想象中好吃。", "差评"),
    ("老板人很好，多送了一瓶水。", "好评"),
    ("要是能选辣度就更好了。", "建议"),
    ("价格有点贵，不过味道确实不错。", "差评"),
    ("第三次点了，一如既往的稳定。", "好评"),
]


def run(name, classify):
    right, bad_format, wrong = 0, 0, []
    for text, expected in CASES:
        got = classify(text).strip()
        if got not in ("好评", "差评", "建议"):   # 不是三个词之一：程序没法直接用，单独记
            bad_format += 1
        if got == expected:
            right += 1
        else:
            wrong.append(f"{text} → {got[:12]}（应为 {expected}）")   # got[:12]：太长的只显示前 12 个字
    print(f"{name}：答对 {right}/{len(CASES)}，格式不对 {bad_format} 条")
    for w in wrong:
        print("   ", w)


if __name__ == "__main__":   # 直接运行才执行；4.13 节 import CASES 时不执行
    run("zero-shot", classify_zero)
    run("few-shot ", classify_few)
