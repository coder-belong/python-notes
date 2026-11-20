# app/response.py（3.4）
from __future__ import annotations


def success(data: object = None, msg: str = "ok") -> dict:
    """成功时把数据包一层：{"code": 200, "msg": msg, "data": data}"""
    return {"code": 200, "msg": msg, "data": data}


# success({"id": 1})          → {"code": 200, "msg": "ok", "data": {"id": 1}}
# success(msg="删除成功")      → {"code": 200, "msg": "删除成功", "data": None}
