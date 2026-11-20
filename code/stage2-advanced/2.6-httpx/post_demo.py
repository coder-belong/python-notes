import httpx                                       # 补：笔记里这段接在 GET 例子后面，单独运行要自己 import

r = httpx.post(
    "https://httpbin.org/post",
    json={"title": "写笔记", "done": False},        # 自动转成 JSON，并加上 Content-Type
    headers={"Authorization": "Bearer my-token"},  # 带 token 之类的请求头
    timeout=10,
)
print(r.json()["json"])                            # {'done': False, 'title': '写笔记'}
print(r.json()["headers"]["Authorization"])        # Bearer my-token
