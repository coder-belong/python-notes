# sandbox.py：在单独的进程里运行模型写的代码：限时间、换目录、出错不影响主程序
import subprocess
import sys
import tempfile


def run_code(code: str, timeout: float = 5) -> tuple[bool, str]:
    """运行一段 Python 代码，返回（成功没有, 输出或报错）。"""
    with tempfile.TemporaryDirectory() as tmp:           # 临时目录：代码在这里跑，跑完整个删掉
        try:
            r = subprocess.run(
                [sys.executable, "-I", "-c", code],      # -I：不读环境变量和当前目录的模块，减少被代码利用的东西
                cwd=tmp, capture_output=True, text=True, timeout=timeout,
                env={},                                  # 不把本机的环境变量（里面有 API key）传给它
            )
        except subprocess.TimeoutExpired:
            return False, f"超时：运行超过 {timeout} 秒，已强制结束"
        out = (r.stdout + r.stderr).strip()
        return r.returncode == 0, out[-1500:]           # 只取最后 1500 个字：报错信息在最后，太长会撑爆上下文


if __name__ == "__main__":
    print(run_code("print(1 + 1)"))
    print(run_code("import os; print(os.environ.get('DEEPSEEK_API_KEY'))"))   # 拿不到 key
    print(run_code("while True: pass", timeout=1))                         # 死循环：1 秒后被杀掉
    print(run_code("1 / 0")[1].splitlines()[-1])                           # 报错：只看最后一行
