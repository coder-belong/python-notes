# tools.py：Agent 能用的工具：查知识库（RAG）、查订单（业务数据）、退款（高风险，要人确认）
import sys

from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import Order, Refund, engine

sys.path.insert(0, "../stage5-rag-demo")   # 借用阶段五的文档切分和混合检索
from load_docs import load_chunks          # noqa: E402
from vector_search import HybridSearcher   # noqa: E402

_kb = HybridSearcher(load_chunks("../stage5-rag-demo/docs"))


class SearchArgs(BaseModel):
    query: str


class OrderArgs(BaseModel):
    order_id: str


class RefundArgs(BaseModel):
    order_id: str
    amount: float
    reason: str


def search_kb(user: str, args: SearchArgs) -> dict:
    hits = _kb.search(args.query, k=2)
    return {"docs": [f"[{c.source} · {c.title}] {c.text}" for c in hits]}


def get_order(user: str, args: OrderArgs) -> dict:
    with Session(engine) as s:
        o = s.get(Order, args.order_id)
        if o is None or o.user != user:            # 只能查自己的订单：权限在代码里查，不靠模型（4.11、6.14 节）
            raise ValueError(f"没有找到订单 {args.order_id}")
        return {"id": o.id, "item": o.item, "amount": o.amount, "status": o.status, "late_minutes": o.late_minutes}


def refund_order(user: str, args: RefundArgs) -> dict:
    with Session(engine) as s:
        o = s.get(Order, args.order_id)
        if o is None or o.user != user:
            raise ValueError(f"没有找到订单 {args.order_id}")
        if o.status == "已退款":
            raise ValueError("这个订单已经退过款了")   # 重复执行也不会退两次（幂等）
        if args.amount > o.amount:
            raise ValueError(f"退款金额不能超过订单金额 {o.amount}")
        o.status = "已退款"
        s.add(Refund(order_id=o.id, amount=args.amount, reason=args.reason))
        s.commit()
        return {"ok": True, "refunded": args.amount}


def schema(name: str, desc: str, model: type[BaseModel]) -> dict:
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": model.model_json_schema()}}


# 名字 → (函数, 参数模型, 是否高风险)
TOOLS = {
    "search_kb": (search_kb, SearchArgs, False),
    "get_order": (get_order, OrderArgs, False),
    "refund_order": (refund_order, RefundArgs, True),
}
SCHEMAS = [
    schema("search_kb", "查豆豆咖啡的规章制度：会员、退款、门店规定", SearchArgs),
    schema("get_order", "按订单号查当前用户的订单：商品、金额、状态、晚到了多少分钟", OrderArgs),
    schema("refund_order", "给订单退款。只有符合退款规则时才调用", RefundArgs),
]
