# tools.py：Agent 能用的三个工具（数据是写死的，不连真接口）
import re

WEATHER = {   # 假数据：城市 → 明天的天气
    "北京": {"天气": "晴", "最高": 6, "最低": -4},
    "上海": {"天气": "小雨", "最高": 13, "最低": 8},
    "广州": {"天气": "多云", "最高": 24, "最低": 17},
}


def get_weather(city: str) -> dict:
    if city not in WEATHER:
        raise ValueError(f"没有 {city} 的天气数据，只支持：{'、'.join(WEATHER)}")
    return {"city": city, **WEATHER[city]}


def calculate(expression: str) -> float:
    if not re.fullmatch(r"[\d\s+\-*/().]+", expression):   # 只允许数字和加减乘除括号，不能执行别的代码
        raise ValueError(f"只支持数字和 + - * / ( )，收到：{expression}")
    return eval(expression)


def send_email(to: str, content: str) -> str:
    print(f"    【已发送邮件】给 {to}：{content[:30]!r}…")   # 真实项目里这里调邮件服务；只打印前 30 个字
    return "发送成功"


FUNCTIONS = {"get_weather": get_weather, "calculate": calculate, "send_email": send_email}

TOOLS = [   # 写法和 4.5 节一样
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查某个城市明天的天气，返回天气、最高和最低气温（摄氏度）",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名，比如 北京"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算一个数学表达式，比如 (13-6)*2",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "给某人发邮件",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "收件人名字"},
                    "content": {"type": "string", "description": "邮件正文"},
                },
                "required": ["to", "content"],
            },
        },
    },
]
