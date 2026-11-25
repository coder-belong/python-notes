# provider.py：认证中心（相当于「微信登录」「公司统一登录」那一方），端口 8501
import secrets
import time
from urllib.parse import urlencode

import jwt
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

app = FastAPI()
ISSUER = "http://localhost:8501"
USERS = {"xiaolin": {"password": "demo-pass", "name": "小林"}}   # 演示用的测试账号
CLIENTS = {   # 事先登记好的网站：client_id → 密钥、允许跳回的地址
    "notes": {"secret": "notes-secret", "redirect_uri": "http://localhost:8502/callback"},
    "quiz": {"secret": "quiz-secret", "redirect_uri": "http://localhost:8503/callback"},
}
SESSIONS: dict[str, str] = {}   # 认证中心自己的登录状态：cookie 值 → 用户名（这就是 SSO 的关键）
CODES: dict[str, dict] = {}     # 授权码 → 发给谁、哪个用户、什么时候过期
TOKENS: dict[str, str] = {}     # access_token → 用户名


def check_client(client_id: str, redirect_uri: str) -> None:
    c = CLIENTS.get(client_id)
    if not c or c["redirect_uri"] != redirect_uri:   # 跳回地址必须和登记的完全一样：防止授权码被发到坏人的网站
        raise HTTPException(400, "client_id 或 redirect_uri 不对")


def issue_code(username: str, client_id: str, redirect_uri: str, state: str) -> RedirectResponse:
    code = secrets.token_urlsafe(16)
    CODES[code] = {"user": username, "client_id": client_id, "expires": time.time() + 60}   # 授权码 60 秒内有效、只能用一次
    return RedirectResponse(f"{redirect_uri}?{urlencode({'code': code, 'state': state})}", status_code=302)


@app.get("/authorize")
def authorize(request: Request, client_id: str, redirect_uri: str, state: str, scope: str = "openid") -> Response:   # 可能返回表单，也可能直接跳转
    check_client(client_id, redirect_uri)
    user = SESSIONS.get(request.cookies.get("sso_session", ""))
    if user:   # 已经在认证中心登录过：不用再输密码，直接发授权码（单点登录）
        return issue_code(user, client_id, redirect_uri, state)
    hidden = "".join(f'<input type="hidden" name="{k}" value="{v}">' for k, v in
                     {"client_id": client_id, "redirect_uri": redirect_uri, "state": state}.items())
    return HTMLResponse(f'<form method="post" action="/login">{hidden}<input name="username"><input name="password" type="password"><button>登录</button></form>')


@app.post("/login")
def login(username: str = Form(), password: str = Form(), client_id: str = Form(), redirect_uri: str = Form(), state: str = Form()) -> RedirectResponse:
    check_client(client_id, redirect_uri)
    if USERS.get(username, {}).get("password") != password:
        raise HTTPException(401, "用户名或密码错误")
    sid = secrets.token_urlsafe(16)
    SESSIONS[sid] = username
    resp = issue_code(username, client_id, redirect_uri, state)
    resp.set_cookie("sso_session", sid, httponly=True)   # 记住「这个浏览器已经在认证中心登录了」
    return resp


@app.post("/token")
def token(code: str = Form(), client_id: str = Form(), client_secret: str = Form(), redirect_uri: str = Form()) -> dict:
    """网站的后端拿授权码来换 token。这一步是服务器对服务器，带着 client_secret，浏览器看不到。"""
    check_client(client_id, redirect_uri)
    if CLIENTS[client_id]["secret"] != client_secret:
        raise HTTPException(401, "client_secret 不对")
    info = CODES.pop(code, None)   # pop：用一次就删掉
    if not info or info["client_id"] != client_id or info["expires"] < time.time():
        raise HTTPException(400, "授权码无效、已用过或已过期")
    access_token = secrets.token_urlsafe(24)
    TOKENS[access_token] = info["user"]
    now = int(time.time())
    id_token = jwt.encode(   # OIDC 多出来的部分：一个写明「这个用户是谁」的 JWT
        {"iss": ISSUER, "aud": client_id, "sub": info["user"], "name": USERS[info["user"]]["name"], "iat": now, "exp": now + 300},
        client_secret, algorithm="HS256",   # 演示用 client_secret 签名；大平台一般用 RS256 私钥签名、公开公钥
    )
    return {"access_token": access_token, "token_type": "Bearer", "id_token": id_token, "expires_in": 3600}


@app.get("/userinfo")
def userinfo(request: Request) -> dict:   # 拿 access_token 查用户信息（OAuth 2.0 的「授权访问资源」）
    user = TOKENS.get(request.headers.get("authorization", "").removeprefix("Bearer "))
    if not user:
        raise HTTPException(401, "token 无效")
    return {"sub": user, "name": USERS[user]["name"]}
