# llm.py
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
MODEL = "deepseek-flash"
NO_THINKING = {"thinking": {"type": "disabled"}}   # 关掉思考模式
