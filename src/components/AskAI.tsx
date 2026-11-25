"use client";

import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import javascript from "highlight.js/lib/languages/javascript";
import json from "highlight.js/lib/languages/json";
import python from "highlight.js/lib/languages/python";
import sql from "highlight.js/lib/languages/sql";
import { Marked } from "marked";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { apiBase, apiGet } from "@/lib/account";

import "./AskAI.css";

hljs.registerLanguage("python", python);
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("json", json);
hljs.registerLanguage("sql", sql);

/** 选中的文字太长就不出按钮：问一段就够了，整节内容后端本来就带着。 */
const MAX_QUOTE = 3000;
/** 这一节的正文最多发这么多字（后端也有同样的上限）。 */
const MAX_SECTION = 60_000;
/** 每个 token 是不是管理员：换节时组件会重建，记住结果就不用每节都问一次后端。 */
const adminCache = new Map<string, boolean>();
const QUICK = ["解释一下这段", "举个能运行的例子", "这里容易错在哪"];
const QUICK_SECTION = ["这一节讲了什么", "这一节的重点是哪几个", "出 3 道题考考我"];

type Msg = { role: "user" | "assistant"; content: string; usage?: Usage; error?: string; stopped?: boolean };
type Usage = { prompt_tokens: number | null; cache_hit_tokens: number | null; completion_tokens: number | null };
type Section = { id: string; title: string; html: string };

const escapeHtml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** 模型的回答是 Markdown：转成 HTML，代码块上色；回答里夹带的 HTML 标签原样显示成文字，不当成页面元素。 */
const markdown = new Marked({
  gfm: true,
  breaks: true,
  renderer: {
    html: ({ text }) => escapeHtml(text),
    code({ text, lang }) {
      // 模型有时不写语言名：在注册过的几种语言里自动猜一个
      const html = lang && hljs.getLanguage(lang) ? hljs.highlight(text, { language: lang }).value : hljs.highlightAuto(text).value;
      return `<pre><code class="hljs">${html}</code></pre>\n`;
    },
    link: ({ href, text }) => `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${text}</a>`,
  },
});

/** 一节的 HTML 转成纯文字，发给后端放进 system。 */
function sectionText(html: string): string {
  const doc = new DOMParser().parseFromString(html, "text/html");
  return (doc.body.textContent ?? "").replace(/\n{3,}/g, "\n\n").slice(0, MAX_SECTION);
}

/** 第一个问题前面带上选中的内容；追问就只发问题本身。 */
const WIDTH_KEY = "python-notes:ask-ai-width"; // 拖出来的面板宽度，下次打开还是这个宽度
const MIN_WIDTH = 400;
const IS_MAC = typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.platform);
const SHORTCUT = IS_MAC ? "⌘J" : "Ctrl+J";

/** 正文里当前选中的文字和位置；没选中、太长、不在正文里都返回 null。 */
function pickSelection(): { text: string; range: Range } | null {
  const sel = window.getSelection();
  const text = sel?.toString().trim() ?? "";
  const node = sel?.anchorNode;
  const el = node instanceof Element ? node : node?.parentElement;
  if (!sel || sel.rangeCount === 0 || !text || text.length > MAX_QUOTE || !el?.closest(".sec-main")) return null;
  return { text, range: sel.getRangeAt(0).cloneRange() };
}

/** 回到原文：滚到那一段，用浏览器的「自定义高亮」标两秒（不改选区，也就不会又弹出问 AI 按钮）。 */
function flashRange(range: Range): void {
  const target = range.startContainer instanceof Element ? range.startContainer : range.startContainer.parentElement;
  target?.scrollIntoView({ behavior: "smooth", block: "center" });
  if (typeof CSS === "undefined" || !("highlights" in CSS)) return;
  CSS.highlights.set("ask-ai-jump", new Highlight(range));
  window.setTimeout(() => CSS.highlights.delete("ask-ai-jump"), 2200);
}

function withQuote(quote: string, question: string): string {
  return `我在这一节里选中了下面这段：\n"""\n${quote}\n"""\n\n${question}`;
}

/**
 * 问 AI：在正文里选中一段文字，旁边出一个「问 AI」按钮，点了在右侧打开对话面板，回答流式显示，可以追问。
 * 只有管理员能用（后端 /ai/chat 也会检查）。
 */
export default function AskAI({ token, section }: { token: string; section: Section }) {
  const [isAdmin, setIsAdmin] = useState(() => adminCache.get(token) ?? false);
  const [btn, setBtn] = useState<{ x: number; y: number; text: string; range: Range } | null>(null);
  const [open, setOpen] = useState(false);
  const [closing, setClosing] = useState(false); // 正在播放滑出动画，播完再真正关掉
  const [quote, setQuote] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const stickRef = useRef(true); // 列表是不是停在最底部：用户往上翻着看时，新内容不再把它拽回底部
  const quoteRangeRef = useRef<Range | null>(null); // 选中内容在正文里的位置，「回到原文」用
  const lastDownRef = useRef(0); // 上次在拖动条上按下的时间：两次挨得很近就当双击
  const [width, setWidth] = useState<number | null>(() => {
    try {
      return Number(localStorage.getItem(WIDTH_KEY)) || null; // null：用 CSS 里的默认宽度
    } catch {
      return null;
    }
  });
  const saveWidth = (w: number | null) => {
    setWidth(w);
    try {
      if (w) localStorage.setItem(WIDTH_KEY, String(w));
      else localStorage.removeItem(WIDTH_KEY);
    } catch {
      // 存不了就只在这次生效
    }
  };

  // 拖面板左边缘调宽：按下后跟着鼠标走，松开时记下来
  const startResize = (e: React.PointerEvent) => {
    e.preventDefault();
    const now = Date.now();
    if (now - lastDownRef.current < 350) {
      saveWidth(null); // 双击：恢复默认宽度
      return;
    }
    lastDownRef.current = now;
    const handle = e.currentTarget as HTMLElement;
    handle.setPointerCapture(e.pointerId);
    document.body.classList.add("ask-ai-resizing");
    let w = width;
    const move = (ev: PointerEvent) => {
      w = Math.round(Math.min(Math.max(window.innerWidth - ev.clientX, MIN_WIDTH), window.innerWidth - 48));
      setWidth(w);
    };
    const up = () => {
      handle.removeEventListener("pointermove", move);
      handle.removeEventListener("pointerup", up);
      document.body.classList.remove("ask-ai-resizing");
      saveWidth(w);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", up);
  };
  const text = useMemo(() => sectionText(section.html), [section.html]);

  useEffect(() => {
    let alive = true;
    if (adminCache.has(token)) return;
    apiGet<{ is_admin?: boolean }>("/auth/me", token)
      .then((me) => {
        adminCache.set(token, !!me.is_admin);
        if (alive) setIsAdmin(!!me.is_admin);
      })
      .catch(() => alive && setIsAdmin(false));
    return () => {
      alive = false;
    };
  }, [token]);

  // 选中文字：正文里选中了一段，就在选区右下角放一个「问 AI」按钮
  useEffect(() => {
    if (!isAdmin) return;
    let timer = 0;
    const check = () => {
      const picked = pickSelection();
      if (!picked) {
        setBtn(null);
        return;
      }
      const rect = picked.range.getBoundingClientRect();
      const x = Math.min(Math.max(rect.right - 40, 8), window.innerWidth - 90);
      const y = rect.bottom + 44 > window.innerHeight ? rect.top - 38 : rect.bottom + 8;
      setBtn({ x, y, ...picked });
    };
    const onChange = () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(check, 250); // 拖着选的过程中不出按钮，停下来再出
    };
    const hide = () => setBtn(null); // 按钮是固定定位的，页面一滚就对不上选区了，先藏起来
    document.addEventListener("selectionchange", onChange);
    window.addEventListener("scroll", hide, { passive: true });
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("selectionchange", onChange);
      window.removeEventListener("scroll", hide);
    };
  }, [isAdmin]);

  // 换了一节时组件会整个重建（外面用 section.id 做 key），对话自然清空；这里把还在进行的请求停掉
  useEffect(() => () => abortRef.current?.abort(), []);

  // 新内容出来时滚到底（用户往上翻了就不动）
  useEffect(() => {
    const list = listRef.current;
    if (list && stickRef.current) list.scrollTop = list.scrollHeight;
  }, [msgs]);

  const close = useCallback(() => {
    setClosing(true);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.setTimeout(
      () => {
        setOpen(false);
        setClosing(false);
      },
      reduce ? 0 : 220, // 和 CSS 里滑出动画的时长一样
    );
  }, []);

  // Esc 关闭面板
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        close();
      }
    };
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [open, close]);

  const startWithSelection = (picked: { text: string; range: Range }) => {
    abortRef.current?.abort();
    setQuote(picked.text);
    quoteRangeRef.current = picked.range;
    setMsgs([]);
    setInput("");
    setOpen(true);
    setClosing(false);
    stickRef.current = true;
    setBtn(null);
    window.getSelection()?.removeAllRanges();
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  // 右下角的入口：不带选中内容打开面板；之前关掉的对话还在，接着聊
  const openPanel = () => {
    setOpen(true);
    setClosing(false);
    stickRef.current = true;
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  // 快捷键 ⌘J / Ctrl+J：面板开着就关；正文里选了文字就带上它开始问；都没有就打开面板
  const shortcutRef = useRef<() => void>(() => {});
  useEffect(() => {
    shortcutRef.current = () => {
      if (open && !closing) {
        close();
        return;
      }
      const picked = pickSelection();
      if (picked) startWithSelection(picked);
      else openPanel();
    };
  });
  useEffect(() => {
    if (!isAdmin) return;
    const onKey = (e: KeyboardEvent) => {
      if ((IS_MAC ? e.metaKey : e.ctrlKey) && !e.shiftKey && !e.altKey && e.key.toLowerCase() === "j") {
        e.preventDefault();
        shortcutRef.current();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isAdmin]);

  // 点引用的内容：关掉面板，正文滚回那一段并高亮
  const jumpToQuote = () => {
    const range = quoteRangeRef.current;
    if (!range?.startContainer.isConnected) return;
    close();
    window.setTimeout(() => flashRange(range), 240); // 等面板滑出去再滚
  };

  const send = useCallback(
    async (question: string) => {
      const q = question.trim();
      if (!q || busy) return;
      const history: Msg[] = [...msgs.filter((m) => !m.error), { role: "user", content: q }];
      setMsgs([...history, { role: "assistant", content: "" }]);
      setInput("");
      if (inputRef.current) inputRef.current.style.height = "auto"; // 发出去后输入框缩回一行
      setBusy(true);
      stickRef.current = true;

      // 发给后端的历史：第一个问题带上选中的内容
      const payload = history.map((m, i) => ({
        role: m.role,
        content: i === 0 && quote ? withQuote(quote, m.content) : m.content,
      }));
      const update = (patch: Partial<Msg>) =>
        setMsgs((list) => [...list.slice(0, -1), { ...list[list.length - 1], ...patch }]);

      const controller = new AbortController();
      abortRef.current = controller;
      let answer = "";
      try {
        const res = await fetch(`${apiBase()}/ai/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ section_title: section.title, section_text: text, messages: payload }),
          signal: controller.signal,
        });
        if (!res.ok || !res.body) {
          const err = (await res.json().catch(() => null)) as { msg?: string } | null;
          update({ error: err?.msg ?? `请求失败（${res.status}）` });
          return;
        }
        // 读 SSE：按空行切成一条条消息，每条是 event: 和 data: 两行
        const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
        let buf = "";
        for (;;) {
          const { value, done } = await reader.read();
          if (done) break;
          buf += value;
          const parts = buf.split("\n\n");
          buf = parts.pop() ?? "";
          for (const part of parts) {
            const event = part.match(/^event: (.*)$/m)?.[1];
            const data = part.match(/^data: (.*)$/m)?.[1];
            if (!event || !data) continue;
            const payload = JSON.parse(data);
            if (event === "delta") {
              answer += payload.text;
              update({ content: answer });
            } else if (event === "done") {
              update({ usage: payload });
            } else if (event === "error") {
              update({ error: payload.msg });
            }
          }
        }
      } catch {
        if (controller.signal.aborted) update({ stopped: true });
        else update({ error: "连不上服务器，检查一下网络" });
      } finally {
        if (abortRef.current === controller) abortRef.current = null;
        setBusy(false);
      }
    },
    [busy, msgs, quote, section.title, text, token],
  );

  const newChat = () => {
    abortRef.current?.abort();
    setMsgs([]);
    setInput("");
    inputRef.current?.focus();
  };

  if (!isAdmin) return null;

  const last = msgs.length - 1;

  return (
    <>
      {btn && (
        <button
          type="button"
          className="ask-ai-btn"
          style={{ left: btn.x, top: btn.y }}
          onMouseDown={(e) => e.preventDefault()} // 不让点击把选区取消掉
          onClick={() => btn && startWithSelection(btn)}
          title={open ? "用新选中的内容开始新对话" : undefined}
        >
          <Sparkle />
          {open ? "问这段" : "问 AI"}
        </button>
      )}

      {!open && (
        <button type="button" className="ask-ai-fab" onClick={openPanel} title={`问 AI（${SHORTCUT}）：问这一节的问题；先选中正文再按 ${SHORTCUT}，会带上选中的内容`} aria-label="问 AI">
          <Sparkle />
        </button>
      )}

      {open && <div className={`ask-ai-mask ${closing ? "closing" : ""}`} onClick={close} aria-hidden="true" />}

      {open && (
        <section
          className={`ask-ai ${closing ? "closing" : ""}`}
          style={width ? { width: `min(${width}px, 100vw)` } : undefined}
          aria-label="问 AI"
        >
          <div
            className="ask-ai-resize"
            onPointerDown={startResize}
            title="拖动调整宽度，双击恢复默认"
            aria-hidden="true"
          />
          <header className="ask-ai-head">
            <span className="ask-ai-logo" aria-hidden="true">
              <Sparkle />
            </span>
            <div className="ask-ai-title">
              <b>问 AI</b>
              <span>{section.title}</span>
            </div>
            {msgs.length > 0 && (
              <button type="button" className="ask-ai-icon" onClick={newChat} title="新对话：清空对话，选中的内容保留">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
                </svg>
              </button>
            )}
            <button type="button" className="ask-ai-icon" onClick={close} aria-label="关闭（Esc）" title="关闭（Esc）">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                <path d="M6 6l12 12M18 6 6 18" />
              </svg>
            </button>
          </header>

          <div
            className="ask-ai-list"
            ref={listRef}
            onScroll={(e) => {
              const el = e.currentTarget;
              stickRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
            }}
          >
            {quote && (
              <figure
                className="ask-ai-quote"
                role="button"
                tabIndex={0}
                title="回到原文"
                onClick={jumpToQuote}
                onKeyDown={(e) => e.key === "Enter" && jumpToQuote()}
              >
                <figcaption>
                  选中的内容<span>点击回到原文 ↩</span>
                </figcaption>
                <blockquote>{quote}</blockquote>
              </figure>
            )}
            {msgs.length === 0 && (
              <div className="ask-ai-empty">
                {!quote && (
                  <p className="ask-ai-tip">
                    直接问这一节的问题；也可以先在正文里选中一段，点旁边的「问 AI」，回答会针对那一段。
                  </p>
                )}
                <p>可以这样问：</p>
                <div className="ask-ai-quick">
                  {(quote ? QUICK : QUICK_SECTION).map((q) => (
                    <button key={q} type="button" onClick={() => send(q)}>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {msgs.map((m, i) =>
              m.role === "user" ? (
                <div key={i} className="ask-ai-q">
                  {m.content}
                </div>
              ) : (
                <div key={i} className="ask-ai-a">
                  <div className="ask-ai-body">
                    {m.content ? (
                      <div
                        className={`ask-ai-md ${busy && i === last ? "streaming" : ""}`}
                        dangerouslySetInnerHTML={{ __html: markdown.parse(m.content) as string }}
                      />
                    ) : (
                      !m.error &&
                      !m.stopped && (
                        <span className="ask-ai-dots" aria-label="正在回答">
                          <i />
                          <i />
                          <i />
                        </span>
                      )
                    )}
                    {m.error && <p className="ask-ai-err">{m.error}</p>}
                    {m.stopped && <p className="ask-ai-meta">已停止</p>}
                    {m.usage && (
                      <p className="ask-ai-meta">
                        输入 {m.usage.prompt_tokens} token（缓存命中 {m.usage.cache_hit_tokens ?? 0}）· 输出{" "}
                        {m.usage.completion_tokens}
                      </p>
                    )}
                  </div>
                </div>
              ),
            )}
          </div>

          <form
            className="ask-ai-form"
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
          >
            <div className="ask-ai-box">
              <textarea
                ref={inputRef}
                value={input}
                rows={1}
                placeholder={msgs.length ? "继续追问…" : "想问什么？"}
                onChange={(e) => {
                  setInput(e.target.value);
                  // 输入框跟着内容长高，最多 6 行左右
                  e.target.style.height = "auto";
                  e.target.style.height = `${Math.min(e.target.scrollHeight, 140)}px`;
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                    e.preventDefault();
                    send(input);
                  }
                }}
              />
              {busy ? (
                <button type="button" className="ask-ai-send stop" onClick={() => abortRef.current?.abort()} title="停止" aria-label="停止">
                  <svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true">
                    <rect x="5" y="5" width="14" height="14" rx="2" fill="currentColor" />
                  </svg>
                </button>
              ) : (
                <button type="submit" className="ask-ai-send" disabled={!input.trim()} title="发送（Enter）" aria-label="发送">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M12 19V5M5 12l7-7 7 7" />
                  </svg>
                </button>
              )}
            </div>
            <p className="ask-ai-hint">Enter 发送 · Shift + Enter 换行 · {SHORTCUT} 或 Esc 关闭</p>
          </form>
        </section>
      )}
    </>
  );
}

function Sparkle() {
  return (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">
      <path d="M12 2.5c.4 3.9 1.4 6.3 3 7.6 1.4 1.1 3.5 1.7 6.5 1.9-3 .2-5.1.8-6.5 1.9-1.6 1.3-2.6 3.7-3 7.6-.4-3.9-1.4-6.3-3-7.6C7.6 12.8 5.5 12.2 2.5 12c3-.2 5.1-.8 6.5-1.9 1.6-1.3 2.6-3.7 3-7.6Z" />
    </svg>
  );
}
