/**
 * 笔记里的「前端流式接收」演示动图。
 *
 * 正文里写 <div class="stream-demo"></div> 占位，这里把它变成一个会动的演示：
 * 后端发来的 SSE 文字被网络切成一块块（不按事件边界切），前端每读到一块：
 * 拼进 buffer → 按空行切出完整事件 → 最后半个事件留着 → 把 delta 的文字追加到页面。
 * 数据是写死的（4.6 里实际跑出来的回答），不连后端。
 */

import "./StreamDemo.css";

const ANSWER =
  "SSE（Server-Sent Events）是一种基于 HTTP 的服务器推送技术，允许服务器通过单向连接持续向客户端发送文本数据流。它适合实时通知、消息推送等场景，客户端使用 EventSource API 即可接收，并支持自动重连。";

const PIECE = [2, 3, 1, 4, 2, 3, 2, 5, 1, 3];   // 模型每次吐几个字，轮流用
const CUT = [70, 96, 52, 118, 64, 88, 75];      // 网络每块多少个字符，故意不和事件边界对齐
const STEP_MS = 420;

function sse(event: string, data: object): string {
  const body = JSON.stringify(data).replace(/":/g, '": ');   // 和后端 json.dumps 的样子一致
  return `event: ${event}\ndata: ${body}\n\n`;
}

/** 后端发出的完整字节流，按网络块切好。 */
function buildChunks(): string[] {
  const events: string[] = [];
  for (let i = 0, k = 0; i < ANSWER.length; k++) {
    const n = PIECE[k % PIECE.length];
    events.push(sse("delta", { text: ANSWER.slice(i, i + n) }));
    i += n;
  }
  events.push(sse("done", { length: ANSWER.length }));
  const all = events.join("");
  const chunks: string[] = [];
  for (let i = 0, k = 0; i < all.length; k++) {
    chunks.push(all.slice(i, i + CUT[k % CUT.length]));
    i += CUT[k % CUT.length];
  }
  return chunks;
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const raw = (s: string) => esc(s).replace(/\n/g, '<i class="nl">↵</i>');

const TEMPLATE = `
  <div class="sd-head">
    <b>前端流式接收演示</b>
    <span class="sd-status">点「开始」</span>
    <span class="sd-btns">
      <button type="button" class="sd-play">开始</button>
      <button type="button" class="sd-stop" disabled>停止</button>
    </span>
  </div>
  <div class="sd-box">
    <div class="sd-label">① <code>await reader.read()</code> 读到的块（网络怎么切的就怎么来，不管事件边界）</div>
    <div class="sd-reads"></div>
  </div>
  <div class="sd-box">
    <div class="sd-label">② <code>buffer.split("\\n\\n")</code> 切出的完整事件，和 <code>events.pop()</code> 留下的半个</div>
    <div class="sd-split"></div>
  </div>
  <div class="sd-box sd-page-box">
    <div class="sd-label">③ <code>onText(data.text)</code> 追加到页面上</div>
    <div class="sd-page"></div>
  </div>
`;

function mount(root: HTMLElement): () => void {
  root.innerHTML = TEMPLATE;
  const $ = <T extends HTMLElement>(sel: string) => root.querySelector(sel) as T;
  const status = $(".sd-status");
  const play = $<HTMLButtonElement>(".sd-play");
  const stop = $<HTMLButtonElement>(".sd-stop");
  const reads = $(".sd-reads");
  const split = $(".sd-split");
  const page = $(".sd-page");

  const chunks = buildChunks();
  let timer = 0;
  let step = 0;
  let buffer = "";
  let text = "";

  const showPage = (tail = '<i class="sd-caret"></i>') => {
    page.innerHTML = esc(text) + tail;
  };

  const finish = (label: string, tail: string) => {
    window.clearTimeout(timer);
    timer = 0;
    status.textContent = label;
    play.textContent = "重播";
    play.disabled = false;
    stop.disabled = true;
    showPage(tail);
  };

  const tick = () => {
    if (step >= chunks.length) {
      finish("读完了：reader.read() 返回 done: true，循环结束", "");
      return;
    }
    const chunk = chunks[step++];
    buffer += chunk;
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    // ① 最近几块
    const row = document.createElement("div");
    row.className = "sd-read";
    row.innerHTML = `<em>第 ${step} 块</em><span>${raw(chunk)}</span>`;
    reads.appendChild(row);
    while (reads.children.length > 3) reads.firstElementChild?.remove();

    // ② 这一块切出了哪些事件
    const chips: string[] = [];
    let doneTail = "";
    for (const block of events) {
      const event = block.match(/^event: (.*)$/m)?.[1];
      const data = JSON.parse(block.match(/^data: (.*)$/m)?.[1] ?? "{}") as { text?: string; length?: number };
      if (event === "delta" && data.text) {
        text += data.text;
        chips.push(`<span class="sd-chip">delta「${esc(data.text)}」</span>`);
      }
      if (event === "done") {
        chips.push(`<span class="sd-chip done">done · 共 ${data.length} 个字</span>`);
        doneTail = `<span class="sd-end">[完成] 共 ${data.length} 个字</span>`;
      }
    }
    split.innerHTML =
      (chips.length ? chips.join("") : '<span class="sd-none">这一块里没有完整的事件</span>') +
      (buffer ? `<div class="sd-left">留着：<span>${raw(buffer)}</span></div>` : "");

    // ③ 页面
    status.textContent = `第 ${step} / ${chunks.length} 块`;
    if (doneTail) {
      finish("收到 done 事件：说完了", doneTail);
      return;
    }
    showPage();
    timer = window.setTimeout(tick, STEP_MS);
  };

  const start = () => {
    window.clearTimeout(timer);
    step = 0;
    buffer = "";
    text = "";
    reads.innerHTML = "";
    split.innerHTML = "";
    showPage();
    play.disabled = true;
    stop.disabled = false;
    timer = window.setTimeout(tick, 200);
  };

  play.onclick = start;
  stop.onclick = () =>
    finish(
      "controller.abort()：fetch 抛 AbortError，后端检测到断开就停",
      '<span class="sd-end err">[已取消] AbortError</span>',
    );

  // 第一次滚到眼前时自动播一遍
  const io = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) {
      io.disconnect();
      start();
    }
  }, { threshold: 0.5 });
  io.observe(root);

  return () => {
    io.disconnect();
    window.clearTimeout(timer);
  };
}

/** 把正文里所有 .stream-demo 占位变成演示，返回清理函数。 */
export function mountStreamDemos(): () => void {
  const cleanups = Array.from(document.querySelectorAll<HTMLElement>(".content .stream-demo")).map(mount);
  return () => cleanups.forEach((c) => c());
}
