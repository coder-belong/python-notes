# vision_demo.py：让模型「看图」：把小票图片转成 JSON，再用代码核对金额
import base64
import sys

from openai import OpenAI
from pydantic import BaseModel

from llm import MODEL, NO_THINKING, client


class Item(BaseModel):
    name: str
    qty: int
    price: float        # 这一行的金额


class Receipt(BaseModel):
    shop: str
    items: list[Item]
    total: float        # 合计
    paid: float         # 实付


def image_message(path: str, question: str) -> list[dict]:
    """图片转成 base64 的 data URL，和文字一起放进同一条 user 消息里。"""
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return [{
        "role": "user",
        "content": [
            {"type": "text", "text": question},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ],
    }]


ASK = """读这张小票，只输出 json：
{"shop": "店名", "items": [{"name": "商品", "qty": 数量, "price": 金额}], "total": 合计, "paid": 实付}"""

def read_receipt(api: OpenAI, model: str, **extra) -> Receipt:
    resp = api.chat.completions.create(
        model=model,
        messages=image_message("images/receipt.png", ASK),
        response_format={"type": "json_object"},
        **extra,
    )
    raw = resp.choices[0].message.content
    print(raw)
    return Receipt.model_validate_json(raw)                        # 和 4.4 节一样：先校验格式


if sys.argv[1:] == ["local"]:
    # 本机 Ollama 里能看图的小模型（4.13 节）：数据不出本机
    api = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    r = read_receipt(api, "modelscope.cn/ggml-org/Qwen2.5-VL-3B-Instruct-GGUF:Q4_K_M", temperature=0)
else:
    r = read_receipt(client, MODEL, extra_body=NO_THINKING)       # DeepSeek：和平时调用一样，只是消息里多了图片

calc = round(sum(i.price for i in r.items), 2)                    # 模型读的数字，用代码再核一遍
print(f"逐项加起来 {calc}，小票上的合计 {r.total}：{'对得上' if calc == r.total else '对不上，要人工看一下'}")
