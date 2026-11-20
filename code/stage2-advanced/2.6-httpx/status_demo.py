import httpx                  # 补：单独运行要自己 import

r = httpx.get("https://httpbin.org/status/404", timeout=10)
print(r.status_code)          # 404   不会因为 404 报错

try:
    r.raise_for_status()
except httpx.HTTPStatusError as e:
    print("请求失败：", e.response.status_code)   # 请求失败： 404
