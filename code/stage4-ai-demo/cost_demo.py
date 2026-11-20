# cost_demo.py
from llm import MODEL, NO_THINKING, client

PRICE = {"hit": 0.006, "miss": 0.3, "output": 1.2}   # deepseek-flash 高峰价，美元 / 百万 token


def cost_usd(usage):
    hit = usage.prompt_cache_hit_tokens       # 输入里命中缓存的 token
    miss = usage.prompt_cache_miss_tokens     # 输入里没命中的 token
    out = usage.completion_tokens             # 输出的 token
    return (hit * PRICE["hit"] + miss * PRICE["miss"] + out * PRICE["output"]) / 1_000_000


rules = "你是 todo 应用的客服。规则：" + "回答要礼貌、简短，只回答和 todo 应用有关的问题。" * 50   # 故意弄一段很长的 system
for q in ["怎么新建任务？", "怎么删除任务？"]:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": rules}, {"role": "user", "content": q}],
        extra_body=NO_THINKING,
    )
    u = resp.usage
    print(u.prompt_cache_hit_tokens, u.prompt_cache_miss_tokens, u.completion_tokens, f"{cost_usd(u):.6f}")
# 0 767 25 0.000260      第一次：767 个输入 token 全没命中
# 512 255 22 0.000106    第二次：开头一样的 512 个命中缓存，钱少了一半多
