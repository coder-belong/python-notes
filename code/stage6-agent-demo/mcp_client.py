# mcp_client.py：启动 MCP 服务，拿到它的工具，交给模型用
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
SERVER = StdioServerParameters(command=sys.executable, args=["weather_server.py"])   # 怎么启动服务：用当前的 python 跑它


async def main() -> None:
    async with stdio_client(SERVER) as (read, write), ClientSession(read, write) as session:
        await session.initialize()                    # 握手：互相告诉对方支持哪些功能
        listed = await session.list_tools()           # ① 问服务有哪些工具
        for t in listed.tools:
            print("服务提供的工具：", t.name, json.dumps(t.input_schema, ensure_ascii=False)[:80])

        # ② 转成 4.5 节的 tools 格式：MCP 的 input_schema 就是 JSON Schema，直接放进 parameters
        tools = [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.input_schema}}
                 for t in listed.tools]

        messages = [{"role": "user", "content": "明天广州天气怎么样？"}]
        while True:
            msg = (await client.chat.completions.create(
                model="deepseek-flash", messages=messages, tools=tools,
                extra_body={"thinking": {"type": "disabled"}},
            )).choices[0].message
            if not msg.tool_calls:
                print(msg.content)
                break
            messages.append(msg)
            for call in msg.tool_calls:   # ③ 模型要调工具：不在本地执行，而是发给 MCP 服务执行
                result = await session.call_tool(call.function.name, json.loads(call.function.arguments))
                text = " ".join(result.content[0].text.split())   # 返回的是带换行缩进的 JSON 文字，压成一行好看些
                print("MCP 服务返回：", text)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": text})


asyncio.run(main())
