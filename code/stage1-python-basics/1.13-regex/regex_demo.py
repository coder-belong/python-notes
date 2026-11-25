# regex_demo.py
import re

text = "订单 A1024 金额 ¥1,299.50，联系人 13812345678；订单 B77 金额 ¥88，联系人 13900001111"

# ① 找第一个：re.search，找不到返回 None
m = re.search(r"\d{11}", text)          # \d 一个数字，{11} 连续 11 个
print(m.group())                         # 13812345678

# ② 找全部：re.findall，返回列表
print(re.findall(r"1[3-9]\d{9}", text))  # ['13812345678', '13900001111']   [3-9]：3 到 9 中的一个

# ③ 分组：( ) 括起来的部分单独取出来
for order, amount in re.findall(r"订单 (\w+) 金额 ¥([\d,.]+)", text):   # \w 字母数字下划线，+ 一个或多个
    print(order, float(amount.replace(",", "")))
# A1024 1299.5
# B77 88.0

# ④ 替换：re.sub
print(re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", text))   # \1 \2：第 1、2 个分组的内容
# 订单 A1024 金额 ¥1,299.50，联系人 138****5678；订单 B77 金额 ¥88，联系人 139****1111

# ⑤ 整串检查：re.fullmatch，整个字符串都要符合才算
for s in ["2026-11-25", "2026-1-5", "2026-11-25 10:00"]:
    print(s, bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)))
# 2026-11-25 True
# 2026-1-5 False
# 2026-11-25 10:00 False

# ⑥ 切分：re.split，按多种分隔符切
print(re.split(r"[,，;；\s]+", "苹果, 香蕉，橙子;  西瓜"))   # [ ] 里任选一个，+ 连着好几个算一次
# ['苹果', '香蕉', '橙子', '西瓜']

# ⑦ 贪婪和非贪婪：.* 尽量多匹配，.*? 尽量少匹配
html = "<b>加粗</b> 和 <b>又一个</b>"
print(re.findall(r"<b>(.*)</b>", html))    # ['加粗</b> 和 <b>又一个']   一口气吃到最后一个 </b>
print(re.findall(r"<b>(.*?)</b>", html))   # ['加粗', '又一个']

# ⑧ 同一个规则用很多次：先 compile
PHONE = re.compile(r"1[3-9]\d{9}")
print(PHONE.findall("a13800000000b15912345678"))   # ['13800000000', '15912345678']
