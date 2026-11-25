# flow_demo.py：用代码当浏览器，一步一步走登录流程，打印每一跳
import httpx

browser = httpx.Client(follow_redirects=False)   # 不自动跳转：每一跳都看清楚；cookie 会自动保存


def go(method: str, url: str, **kw) -> httpx.Response:
    r = browser.request(method, url, **kw)
    where = r.headers.get("location", "")
    print(f"  {method} {url.split('?')[0]} → {r.status_code} {where.split('?')[0]}{'?' + where.split('?')[1][:40] + '…' if '?' in where else ''}")
    return r


print("1. 第一次登录笔记网站")
r = go("GET", "http://localhost:8502/login")                 # 笔记网站把浏览器带到认证中心
r = go("GET", r.headers["location"])                         # 认证中心：没登录过，返回登录表单
form = dict(x.split('" value="') for x in r.text.split('name="')[1:4])   # 取出表单里的隐藏字段（演示用的简单解析）
form = {k: v.split('"')[0] for k, v in form.items()}
r = go("POST", "http://localhost:8501/login", data={**form, "username": "xiaolin", "password": "demo-pass"})
callback_url = r.headers["location"]
r = go("GET", callback_url)                                  # 带着授权码回到笔记网站，后端换 token
print("  ", go("GET", "http://localhost:8502/").text)

print("2. 再登录题库网站（单点登录）")
r = go("GET", "http://localhost:8503/login")
r = go("GET", r.headers["location"])                         # 认证中心：已经登录过，直接发授权码，不出表单
r = go("GET", r.headers["location"])
print("  ", go("GET", "http://localhost:8503/").text)

print("3. 几种攻击")
print("  重复使用授权码：", browser.get(callback_url).json())
print("  伪造 state：", browser.get("http://localhost:8502/callback?code=x&state=fake").json())
print("  换成坏人的跳回地址：", browser.get("http://localhost:8501/authorize?client_id=notes&redirect_uri=http://evil.test/cb&state=1").json())
