# lc_llm.py：LangChain 版的模型对象，后面几个文件都 import 它
import os

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-flash",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",            # 和 llm.py 一样：DeepSeek 兼容 OpenAI 接口
    extra_body={"thinking": {"type": "disabled"}},  # 关思考
)
