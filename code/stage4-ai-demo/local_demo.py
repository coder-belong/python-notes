# local_demo.py：本机用 Ollama 跑一个小模型，代码和调 DeepSeek 一样，只换地址和模型名
import time

from openai import OpenAI

from eval_demo import CASES          # 4.9 节的 12 条评测集
from fewshot_demo import EXAMPLES, FEW, classify_few

local = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")   # Ollama 兼容 OpenAI 接口；key 随便填，不校验
LOCAL_MODEL = "modelscope.cn/Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M"     # 通义千问 1.5B，4 位量化，约 1.1GB

# ① 普通对话
start = time.perf_counter()
resp = local.chat.completions.create(model=LOCAL_MODEL, messages=[{"role": "user", "content": "用一句话介绍 Python"}])
print(f"{time.perf_counter() - start:.1f}s", resp.choices[0].message.content)


# ② 用 4.9 节的评测集比一比：同样的 few-shot 写法，本地小模型答对几条
def classify_local(text: str) -> str:
    r = local.chat.completions.create(
        model=LOCAL_MODEL,
        messages=[{"role": "system", "content": FEW}, *EXAMPLES, {"role": "user", "content": text}],
        max_tokens=5,
    )
    return r.choices[0].message.content.strip()


for name, classify in [("本地 1.5B", classify_local), ("DeepSeek", classify_few)]:
    start = time.perf_counter()
    wrong = [(t, got) for t, want in CASES if (got := classify(t).strip()) != want]   # := 一边赋值一边判断：got 后面还要用
    print(f"{name}：答对 {len(CASES) - len(wrong)}/{len(CASES)}，共 {time.perf_counter() - start:.1f}s  答错：{wrong}")
