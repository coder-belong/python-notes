import httpx

r = httpx.get("https://httpbin.org/get", params={"q": "python", "page": 1}, timeout=10)
print(r.status_code)          # 200
print(r.url)                  # https://httpbin.org/get?q=python&page=1   params 自动拼进网址
data = r.json()               # 响应体按 JSON 解析成 dict，等于 json.loads(r.text)
print(data["args"])           # {'page': '1', 'q': 'python'}
