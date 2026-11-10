# Python 入门笔记

基础语法 → FastAPI 写接口 → SQLAlchemy 连数据库 → pytest 测试。用 Next.js 维护，导出成一个可以双击打开的 HTML。

## 日常怎么用

| 想做什么 | 怎么做 |
|---|---|
| 改笔记内容 | 编辑 `content/notes.md`（普通 Markdown） |
| 边改边看 | `npm run dev`，打开 http://localhost:3100 ，保存后自动刷新 |
| 生成 HTML | `npm run build`，产物是 `dist/Python入门笔记.html`，双击打开，也可以单独拷走 |

第一次用先装依赖：`npm install`。

## Markdown 的写法约定

- 第一个 `# 一级标题` 是书名，下面的段落是开头导语。
- `# 第X部分：...` 是分组，左侧目录按它分组；它下面、第一个 `##` 之前的段落是这一部分的导语。
- 每个 `## 二级标题` 是一节：左侧目录一项、带「学完了」勾选、单独统计学习时长。
- 代码块写上语言（```python、```bash），构建时自动上色。
- 表格里要写 `|` 时，写成 `\|`。

## 学习时长

- 页面在前台、窗口有焦点、并且 90 秒内有过滚动 / 鼠标 / 键盘操作时，每秒记 1 秒；切走或离开会自动暂停。
- 同时记到「今天」和「当前读到的那一节」上。侧边栏顶部只有一个「学习统计」入口（显示状态和今天的时长），点开弹窗看本次计时、今天、累计、连续学习天数、最近 7 天和每节用时；Esc 或点空白处关闭。
- 记录存在浏览器的 localStorage 里：只在这台电脑的这个浏览器有效，换浏览器、清浏览器数据都会没有。`file://` 打开的 HTML 和 `npm run dev` 的 localhost 是两份独立的记录。

## 目录结构

```
content/notes.md            笔记正文
src/app/page.tsx            构建时读 notes.md，交给 NotesApp
src/lib/notes.ts            Markdown → 按「部分 / 节」拆好的 HTML（代码高亮在这里做）
src/components/NotesApp.tsx 页面：目录、正文、勾选、复制按钮、当前小节
src/components/StudyPanel.tsx  侧边栏的学习时长面板
src/lib/use-study.ts        计时逻辑
src/lib/study-store.ts      学习记录的读写和格式化
src/styles/globals.css      样式（构建时直接写进页面）
scripts/single-html.mjs     把 out/ 打成一个 HTML
```
