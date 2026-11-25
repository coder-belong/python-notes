# website.py：接入认证中心的网站。同一份代码跑两个：笔记网站 8502、题库网站 8503（用环境变量区分）
import os
import secrets
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

CLIENT_ID = os.environ["CLIENT_ID"]                 # notes 或 quiz
CLIENT_SECRET = os.environ["CLIENT_SECRET"]         # 只放在后端，绝不能给前端
PORT = os.environ["PORT"]
PROVIDER = "http://localhost:8501"
REDIRECT_URI = f"http://localhost:{PORT}/callback"
COOKIE = f"{CLIENT_ID}_session"                     # 同一个 localhost 不同端口的 cookie 是共享的，名字要分开

app = FastAPI()
SESSIONS: dict[str, str] = {}                       # 这个网站自己的登录状态


@app.get("/")
def home(request: Request) -> HTMLResponse:
    name = SESSIONS.get(request.cookies.get(COOKIE, ""))
    return HTMLResponse(f"{CLIENT_ID}：已登录，{name}" if name else f'{CLIENT_ID}：未登录 <a href="/login">用认证中心登录</a>')


@app.get("/login")
def login() -> RedirectResponse:
    state = secrets.token_urlsafe(16)               # 随机数：回来时核对，防止别人伪造回调（CSRF）
    query = urlencode({"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "state": state, "scope": "openid profile"})
    resp = RedirectResponse(f"{PROVIDER}/authorize?{query}", status_code=302)   # ① 把浏览器带到认证中心
    resp.set_cookie(f"{CLIENT_ID}_state", state, httponly=True)
    return resp


@app.get("/callback")
def callback(request: Request, code: str, state: str) -> RedirectResponse:
    if state != request.cookies.get(f"{CLIENT_ID}_state"):   # ③ 核对 state
        raise HTTPException(400, "state 不对，可能是伪造的回调")
    r = httpx.post(f"{PROVIDER}/token", data={              # ④ 后端拿授权码 + 密钥换 token
        "code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "redirect_uri": REDIRECT_URI,
    })
    if r.status_code != 200:
        raise HTTPException(400, f"换 token 失败：{r.json()['detail']}")
    claims = jwt.decode(r.json()["id_token"], CLIENT_SECRET, algorithms=["HS256"],   # ⑤ 校验 id_token：签名、发给谁、谁发的、过期没有
                        audience=CLIENT_ID, issuer=PROVIDER)
    sid = secrets.token_urlsafe(16)
    SESSIONS[sid] = claims["name"]                          # ⑥ 建立这个网站自己的登录状态（也可以签发 3.13 节那样的 JWT）
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(COOKIE, sid, httponly=True)
    return resp
