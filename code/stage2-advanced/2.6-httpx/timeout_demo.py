import httpx                  # 补：单独运行要自己 import

try:
    httpx.get("https://httpbin.org/delay/3", timeout=1)   # 这个地址 3 秒后才返回
except httpx.TimeoutException:
    print("超过 1 秒，超时了")
