# trace_demo.py
import json

from agent import run_agent

answer, trace = run_agent(
    "明天北京和上海的最高气温差几度？发邮件告诉小王。",
    confirm=lambda name, args: True,   # 演示用：自动同意
    log=lambda line: None,             # 不打印过程，只看 trace
)

# 每一步的记录
for t in trace:
    if t["type"] == "llm":
        print(f"第 {t['step']} 步 调模型  {t['ms']:>5} ms  {t['tokens']:>4} token  ${t['usd']:.6f}")
    else:
        print(f"第 {t['step']} 步 {t['name']:<11} {t['ms']:>3} ms  {'成功' if t['ok'] else '失败'}  {t['args'][:30].replace(chr(10), ' ')}")

# 汇总：一个任务花了多少
llm = [t for t in trace if t["type"] == "llm"]
print(f"合计：调模型 {len(llm)} 次，{sum(t['tokens'] for t in llm)} token，"
      f"${sum(t['usd'] for t in llm):.6f}，{sum(t['ms'] for t in trace) / 1000:.1f} 秒")

# 存下来：一行一个任务，以后查问题、做统计都靠它
with open("traces.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({"task": "温差邮件", "answer": answer, "trace": trace}, ensure_ascii=False) + "\n")
