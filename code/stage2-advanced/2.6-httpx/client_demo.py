import httpx                  # 补：单独运行要自己 import

with httpx.Client(base_url="https://httpbin.org", headers={"Authorization": "Bearer my-token"}, timeout=10) as client:
    r1 = client.get("/get")                       # 实际请求 https://httpbin.org/get
    r2 = client.post("/post", json={"a": 1})
    print(r1.status_code, r2.status_code)         # 200 200
