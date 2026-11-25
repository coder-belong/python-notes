# stage3-oauth-demo：3.21 节「第三方登录和单点登录」练习代码

一个认证中心（8501）+ 两个接入它的网站（笔记网站 8502、题库网站 8503），用代码模拟浏览器走一遍 OAuth 2.0 授权码流程、OIDC 和单点登录。只在本机跑，账号密码都是演示用的。

## 准备

```bash
cd code/stage3-oauth-demo
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install fastapi uvicorn httpx pyjwt python-multipart
```

## 运行（开 4 个终端）

```bash
uvicorn provider:app --port 8501
CLIENT_ID=notes CLIENT_SECRET=notes-secret PORT=8502 uvicorn website:app --port 8502
CLIENT_ID=quiz CLIENT_SECRET=quiz-secret PORT=8503 uvicorn website:app --port 8503
python flow_demo.py
```

| 文件 | 内容 |
|---|---|
| `provider.py` | 认证中心：/authorize、/login、/token、/userinfo |
| `website.py` | 接入的网站：/login、/callback、首页 |
| `flow_demo.py` | 走一遍首次登录、单点登录、三种攻击 |
