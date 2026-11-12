# AI 应用开发笔记

从 Python 到 Agent：基础语法 → FastAPI 写接口 → SQLAlchemy 连数据库 → pytest 测试 → AI 应用与 Agent 开发。用 Next.js 维护，导出成一个可以双击打开的 HTML。

## 日常怎么用

| 想做什么 | 怎么做 |
|---|---|
| 改笔记内容 | 编辑 `content/notes.md`（普通 Markdown） |
| 改学习路线 | 编辑 `ROADMAP.md`，首页的「学习路线」从这里读 |
| 边改边看 | `npm run dev`，打开 http://localhost:3100 。改了 `.tsx` 会自动刷新；改了 `notes.md`、`ROADMAP.md`、`globals.css` 要重启 dev |
| 生成 HTML | `npm run build`，产物是 `dist/AI应用开发笔记.html`，双击打开，也可以单独拷走 |

第一次用先装依赖：`npm install`。

## 页面功能

**首页**（网址没有 `#`）

- 继续学习：上次读到哪一节，点进去回到当时的滚动位置。
- 学习热力图：最近一年每天学了多久，颜色越深学得越久。
- 笔记目录：每个部分一张卡片，带完成进度。
- 学习路线：`ROADMAP.md` 里 6 个阶段的勾选清单，打勾的是笔记里已经写了的。

**每一节**（网址 `#节的id`）

- 一次只显示一节；底部「学完了，下一节」会顺手打勾，也可以用上一节 / 下一节卡片。
- 代码块右上角有「复制」按钮。

**侧栏**

- 目录按部分折叠，显示每部分学完几节；右边缘可以拖动调宽度（双击恢复默认），标题不换行，太长显示省略号。
- 标题左边的方框图标把侧栏收起成一条 56px 的窄边（只留展开、学习状态、「⋯」、账号、主题），正文更宽；再点或按 `\` 展开。收起状态会记住。窄屏的侧栏是抽屉，没有这个按钮。
- 标题右边一排图标：
  - 「⋯」：正文字号（14 / 16 / 18 / 20）、更新日志、收起侧栏。不常用的设置都放这里，以后加设置也往这里放；更新日志有没看过的新内容时，按钮上有小红点；
  - 人像是登录 / 注册，登录后显示用户名的第一个字，右下角小点是同步状态（绿：已同步，橙：失败）；
  - 太阳 / 月亮切换浅色和深色，换的时候新颜色从按钮处画圆铺开；没点过就跟随系统。
- 标题下面一行是今天学了多久，点开是学习统计。

**更新日志**

内容在 `content/changelog.md`：每天一个 `## 2026-11-12`，下面一行一条，开头用【新功能】【改进】【笔记】【修复】标类型，最新的写在最上面。改完要重启 `npm run dev`。新加一天后，「⋯」上会出现小红点，打开更新日志后消失。

**专注模式**

- 每节右上角「专注」或按 F 进入：自动全屏，侧栏收起，正文居中。
- 番茄钟平时只是右上角一个小番茄（外圈是进度，不显示时间），鼠标移上去才展开时间和按钮；暂停、休息时一直展开。浏览器不支持全屏（如 iPhone）时只是不全屏，其他照常。
- 番茄钟里可以开白噪音（雨声 / 海浪 / 白噪音，浏览器现场合成，不用音频文件），带音量；专注计时时才响，暂停、休息时自动停，选过的声音下次还在。
- 专注 25 分钟到点响铃、记一个番茄，自动休息 5 分钟；可以暂停、重来、跳过休息。
- 点「退出专注」或按 Esc / F 退出，全屏也一起退出；只想退全屏、留在专注模式，点番茄钟里的全屏按钮。

**快捷键**

| 键 | 作用 |
|---|---|
| ← → | 上一节 / 下一节 |
| F | 进入 / 退出专注模式 |
| \ | 收起 / 展开侧栏（中文输入法下打出来是「、」，要切到英文） |
| Esc | 退出专注模式、关闭弹窗和菜单 |

## 学习时长

- 页面在前台、窗口有焦点、并且 90 秒内有过滚动 / 鼠标 / 键盘操作时，每秒记 1 秒；切走或离开会自动暂停。
- 同时记到「今天」和「当前这一节」上。统计弹窗里有：本次计时、今天、累计、连续学习天数、半年热力图、今天的番茄数、最近 7 天和每节用时。

## 数据存在哪

都存在浏览器的 localStorage 里；登录后学习记录还会同步到账号上（见下面「账号和同步」）：

| key | 内容 |
|---|---|
| `python-notes:study` | 每天学习时长、每节用时、「学完了」、每天的番茄数 |
| `python-notes:reading` | 上次读到的节和滚动位置 |
| `python-notes:prefs` | 主题、字号 |
| `python-notes:side-w` | 侧栏宽度 |
| `python-notes:side-collapsed` | 侧栏是否收起成窄边 |
| `python-notes:changelog-seen` | 看过的最新一条更新日志的日期（用来判断显不显示小红点） |
| `python-notes:ambient` | 专注模式选的白噪音和音量 |
| `python-notes:auth` | 登录后的 token 和用户名 |
| `python-notes:sync` | 还没同步到账号上的学习记录 |

只在这台电脑的这个浏览器有效：换浏览器、清浏览器数据都会没有。双击打开的 HTML（`file://`）和 `npm run dev` 的 localhost 也是两份独立的记录。

## 账号和同步（backend/）

侧栏顶部的人像图标是「登录 / 注册」：注册成功直接登录。登录后学习时长、「学完了」、番茄数每分钟同步到账号上，勾「学完了」和切走页面时马上同步；家里、公司登录同一个账号，看到的是同一份进度。阅读位置、主题、字号还是只存在本机。

- 同步发的是增量（又学了多少秒），后端在账号上累加，两台电脑的时长不会互相覆盖；每批带 `batch_id`，重发只算一次。
- 第一次在某台电脑上登录时，这台电脑原有的记录会整个加到账号上。
- 没登录时照常记在本机；登录后再补传。

后端是 `backend/` 里的 FastAPI + SQLAlchemy，部署在 Vercel（单独一个项目，根目录选 `backend`），数据库用 Neon 的 Postgres。本地开发：

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

本地不配置也能跑：数据库用 `backend/dev.db`（SQLite）。`npm run dev` 打开的页面会连本机的 8000 端口，其他情况（线上、双击打开的 HTML）连线上的后端。

| 接口 | 作用 |
|---|---|
| `POST /auth/register` | 注册，直接返回 token |
| `POST /auth/login` | 登录，返回 token |
| `GET /auth/me` | 当前登录的是谁 |
| `POST /sync` | 发增量、拿回账号的全部学习记录 |

线上要配的环境变量：`JWT_SECRET`（签 token 的密钥，一串随机字符）、`DATABASE_URL`（接 Neon 后自动有）。

## Markdown 的写法约定

- 第一个 `# 一级标题` 是书名，下面的段落是首页开头的导语。
- `# 阶段X：...` 是分组（和 `ROADMAP.md` 的阶段对应），侧栏目录和首页卡片按它分组；它下面、第一个 `##` 之前的段落是这一阶段的导语，显示在这一阶段第一节的顶部。
- 每个 `## 二级标题` 是一节：单独一页、带「学完了」勾选、单独统计学习时长。
- **每节标题后面写一个固定 id**：`## 1.6 迭代器、生成器、装饰器 {#iter-gen-deco}`。学习记录按这个 id 存，以后改标题、改编号、调整顺序都不会丢；新加的节也照这样写一个（小写英文加连字符）。
- 节号写成「阶段.第几节」（1.1、2.5……），每个阶段从 1 开始；插入新节只需要重排本阶段，别的阶段不动。引用其他节写「第 2.5 节」。
- 代码块写上语言（```python、```bash），构建时自动上色。
- 表格里要写 `|` 时，写成 `\|`。

## 目录结构

```
content/notes.md                笔记正文
content/changelog.md            更新日志
ROADMAP.md                      学习路线（首页读「## 阶段…」下面的勾选清单）
src/app/layout.tsx              页面外壳：把样式直接写进页面，<head> 里先套上主题和字号
src/app/page.tsx                构建时读 notes.md，交给 NotesApp
src/lib/notes.ts                Markdown → 按「部分 / 节」拆好的 HTML（代码高亮在这里做），读 ROADMAP 和更新日志
src/lib/study-store.ts          学习记录、阅读位置的读写和格式化
src/lib/legacy-ids.ts           旧版按标题生成的 id → 固定 id，打开页面时自动迁移学习记录
src/lib/use-study.ts            学习计时、「学完了」、番茄数，登录后的同步
src/lib/account.ts              调后端接口、登录信息和待同步记录的读写
src/lib/prefs.ts                主题、字号的读写
src/components/NotesApp.tsx     页面：按 # 切节、侧栏目录、上一节 / 下一节、快捷键、专注模式开关
src/components/Home.tsx         首页
src/components/Heatmap.tsx      学习热力图
src/components/StudyPanel.tsx   学习统计入口和弹窗
src/components/AccountPanel.tsx 账号入口和登录 / 注册弹窗
src/components/FocusBar.tsx     专注模式右上角的番茄钟、全屏按钮
src/components/ThemeToggle.tsx  浅色 / 深色切换按钮和动画
src/components/MoreMenu.tsx      「⋯」菜单：字号、更新日志、收起侧栏
src/components/ChangelogPanel.tsx  更新日志弹窗
src/components/SideResizer.tsx  拖动调侧栏宽度
src/styles/globals.css          样式（构建时直接写进页面）
scripts/single-html.mjs         把 out/ 打成一个 HTML
backend/index.py                Vercel 的入口
backend/app/main.py             接口：注册、登录、同步
backend/app/models.py           表：用户、每天时长、每节时长和「学完了」、同步批次
backend/app/security.py         密码哈希、JWT、「当前登录用户」依赖
backend/app/schemas.py          请求体校验
backend/app/errors.py           统一响应格式 {code, msg, data}
backend/app/db.py               连数据库（本地 SQLite，线上 Postgres）
backend/app/config.py           读环境变量
```
