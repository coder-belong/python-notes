import time

import httpx


def get_with_retry(url: str, retries: int = 3) -> httpx.Response:
    for attempt in range(1, retries + 1):                 # attempt 依次是 1、2、3，打印「第 1 次」更自然
        try:
            r = httpx.get(url, timeout=5)                 # ① 发请求，最多等 5 秒
            should_retry = r.status_code >= 500 or r.status_code == 429   # ② 5xx、429 值得重试
            if not should_retry:                          # 成功，或 404、401 这类重试也没用的
                return r                                  # 直接返回
            print(f"第 {attempt} 次：{r.status_code}")

        except httpx.TransportError as e:                 # ③ 根本没收到响应：超时、断网、连不上
            print(f"第 {attempt} 次：{type(e).__name__}")   # 打印错误类型，比如 ConnectTimeout

        if attempt < retries:                             # ④ 不是最后一次就等一会儿再试
            time.sleep(2 ** (attempt - 1))                # 等 1、2、4 秒……越等越久（指数退避）

    raise RuntimeError(f"重试 {retries} 次都失败了：{url}")   # ⑤ 每次都失败才会走到这里，放弃并报错

try:
    get_with_retry("https://httpbin.org/status/503")      # 这个地址固定返回 503
except RuntimeError as e:
    print(e)
# 第 1 次：503
# 第 2 次：503
# 第 3 次：503
# 重试 3 次都失败了：https://httpbin.org/status/503
