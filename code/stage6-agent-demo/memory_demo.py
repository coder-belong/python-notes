# memory_demo.py

from llm import MODEL, NO_THINKING, client


def chat(messages: list[dict]) -> tuple[str, int]:
    resp = client.chat.completions.create(model=MODEL, messages=messages, extra_body=NO_THINKING, max_tokens=200)
    return resp.choices[0].message.content, resp.usage.prompt_tokens


# ---------- 短期记忆：对话太长时，旧的几轮压成摘要 ----------
SYSTEM = "你是生活助手，回答一两句话。"
KEEP = 2   # 原样保留最近几轮


def compress(summary: str, old: list[dict]) -> str:
    """把旧摘要 + 要丢掉的几轮对话，压成新的摘要。"""
    text = "\n".join(f"{m['role']}: {m['content']}" for m in old)
    prompt = f"已有摘要：{summary or '无'}\n新对话：\n{text}\n\n合并成一份简短摘要，保留用户的个人信息、偏好和已经确定的结论。"
    return chat([{"role": "user", "content": prompt}])[0]


def run_chat(questions: list[str], mode: str) -> None:   # mode：all 全留 / trim 只留最近几轮 / summary 旧的压成摘要
    summary, history = "", []
    for q in questions:
        history.append({"role": "user", "content": q})
        system = SYSTEM + (f"\n之前对话的摘要：{summary}" if summary else "")
        reply, tokens = chat([{"role": "system", "content": system}, *history])
        history.append({"role": "assistant", "content": reply})
        if mode != "all" and len(history) > KEEP * 2:   # 超过 KEEP 轮：去掉最早的一轮（一问一答两条，一起去掉）
            if mode == "summary":
                summary = compress(summary, history[:2])  # 去掉之前先压进摘要
            history = history[2:]
        print(f"{tokens:>4} token  {q} → {reply[:40]}")
    if summary:
        print("摘要：", summary)


QUESTIONS = [
    "我叫小林，对花生过敏。",
    "推荐一部轻松的电影。",
    "周末想去爬山，要带什么？",
    "帮我想个晚饭菜单。",
    "我叫什么？对什么过敏？",
]
for mode in ["all", "trim", "summary"]:
    print(f"--- {mode}")
    run_chat(QUESTIONS, mode)
