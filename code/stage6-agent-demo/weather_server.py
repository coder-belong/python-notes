# weather_server.py：把天气查询做成一个 MCP 服务，任何支持 MCP 的 Agent 都能接
from mcp.server.mcpserver import MCPServer

import tools

server = MCPServer("weather")


@server.tool()   # 和 LangChain 的 @tool 一样：函数名、参数类型、文档字符串自动变成工具描述
def get_weather(city: str) -> dict:
    """查某个城市明天的天气，返回天气、最高和最低气温（摄氏度）"""
    return tools.get_weather(city)


if __name__ == "__main__":
    server.run()   # 默认用 stdio：客户端把它当子进程启动，通过标准输入输出收发消息
