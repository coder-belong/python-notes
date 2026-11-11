# Python 入门笔记

基础语法 → FastAPI 写接口 → SQLAlchemy 连数据库 → pytest 测试。用 Next.js 维护，导出成一个可以双击打开的 HTML。

## 日常怎么用

| 想做什么 | 怎么做 |
|---|---|
| 改笔记内容 | 编辑 `content/notes.md`（普通 Markdown） |
| 改学习路线 | 编辑 `ROADMAP.md`，首页的「学习路线」从这里读 |
| 边改边看 | `npm run dev`，打开 http://localhost:3100 。改了 `.tsx` 会自动刷新；改了 `notes.md`、`ROADMAP.md`、`globals.css` 要重启 dev |
| 生成 HTML | `npm run build`，产物是 `dist/Python入门笔记.html`，双击打开，也可以单独拷走 |

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
- 标题右边的太阳 / 月亮切换浅色和深色，换的时候新颜色从按钮处画圆铺开；没点过就跟随系统。
- 「A− 标准 A+」调正文字号（14 / 16 / 18 / 20）。
- 「学习统计」打开统计弹窗。

**专注模式**

- 每节右上角「专注」或按 F 进入：侧栏收起，正文居中，底部出现番茄钟。
- 专注 25 分钟到点响铃、记一个番茄，自动休息 5 分钟；可以暂停、重来、跳过休息。
- 点「退出专注」或按 Esc / F 退出。

**快捷键**

| 键 | 作用 |
|---|---|
| ← → | 上一节 / 下一节 |
| F | 进入 / 退出专注模式 |
| Esc | 退出专注模式、关闭统计弹窗 |

## 学习时长

- 页面在前台、窗口有焦点、并且 90 秒内有过滚动 / 鼠标 / 键盘操作时，每秒记 1 秒；切走或离开会自动暂停。
- 同时记到「今天」和「当前这一节」上。统计弹窗里有：本次计时、今天、累计、连续学习天数、半年热力图、今天的番茄数、最近 7 天和每节用时。

## 数据存在哪

全部存在浏览器的 localStorage 里，没有后端：

| key | 内容 |
|---|---|
| `python-notes:study` | 每天学习时长、每节用时、「学完了」、每天的番茄数 |
| `python-notes:reading` | 上次读到的节和滚动位置 |
| `python-notes:prefs` | 主题、字号 |
| `python-notes:side-w` | 侧栏宽度 |

只在这台电脑的这个浏览器有效：换浏览器、清浏览器数据都会没有。双击打开的 HTML（`file://`）和 `npm run dev` 的 localhost 也是两份独立的记录。

## Markdown 的写法约定

- 第一个 `# 一级标题` 是书名，下面的段落是首页开头的导语。
- `# 第X部分：...` 是分组，侧栏目录和首页卡片按它分组；它下面、第一个 `##` 之前的段落是这一部分的导语，显示在这部分第一节的顶部。
- 每个 `## 二级标题` 是一节：单独一页、带「学完了」勾选、单独统计学习时长。
- 代码块写上语言（```python、```bash），构建时自动上色。
- 表格里要写 `|` 时，写成 `\|`。

## 目录结构

```
content/notes.md                笔记正文
ROADMAP.md                      学习路线（首页读「## 阶段…」下面的勾选清单）
src/app/layout.tsx              页面外壳：把样式直接写进页面，<head> 里先套上主题和字号
src/app/page.tsx                构建时读 notes.md，交给 NotesApp
src/lib/notes.ts                Markdown → 按「部分 / 节」拆好的 HTML（代码高亮在这里做），读 ROADMAP
src/lib/study-store.ts          学习记录、阅读位置的读写和格式化
src/lib/use-study.ts            学习计时、「学完了」、番茄数
src/lib/prefs.ts                主题、字号的读写
src/components/NotesApp.tsx     页面：按 # 切节、侧栏目录、上一节 / 下一节、快捷键、专注模式开关
src/components/Home.tsx         首页
src/components/Heatmap.tsx      学习热力图
src/components/StudyPanel.tsx   学习统计入口和弹窗
src/components/FocusBar.tsx     专注模式底部的番茄钟
src/components/ThemeToggle.tsx  浅色 / 深色切换按钮和动画
src/components/DisplaySettings.tsx  字号调节
src/components/SideResizer.tsx  拖动调侧栏宽度
src/styles/globals.css          样式（构建时直接写进页面）
scripts/single-html.mjs         把 out/ 打成一个 HTML
```
