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
/** 能不能用问 AI：登录并且累计学习满 30 分钟（管理员不限），后端 /auth/me 算好返回。 */
type Access = { unlocked: boolean; seconds: number; need: number };
/** 已经解锁的 token 记下来：换节时组件会重建，不用每节都问一次后端。没解锁的不记，下次点入口时重新查。 */
const unlockedTokens = new Set<string>();
const UNLOCKED: Access = { unlocked: true, seconds: 0, need: 0 };

function fetchAccess(token: string): Promise<Access> {
  return apiGet<{ ai_unlocked?: boolean; study_seconds?: number; ai_unlock_seconds?: number }>("/auth/me", token).then((me) => {
    const a = { unlocked: !!me.ai_unlocked, seconds: me.study_seconds ?? 0, need: me.ai_unlock_seconds ?? 1800 };
    if (a.unlocked) unlockedTokens.add(token);
    return a;
  });
}
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
const SIDE_KEY = "python-notes:ask-ai-side"; // 左侧对话列表收起了没有
const SIDE_MIN_PANEL = 640; // 面板至少这么宽才放得下左侧列表；窄的时候「历史」改成切换整个视图
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

/** 历史列表里的一条对话（不带消息内容，点开再取）。 */
type ChatSummary = { id: number; title: string; section_id: string; section_title: string; count: number; updated_at: string };
/** 一条历史对话的完整内容。 */
type ChatDetail = { id: number; quote: string | null; messages: Msg[] };
/**
 * 在别的节点开了一条历史对话：先把内容取回来放在这里，再跳到那一节。
 * 组件跟着节重建时直接用它初始化，面板一出来就是打开的、带着消息，中间不会空一下。
 */
let pendingChat: ChatDetail | null = null;
/** 列表缓存一份：换节时组件会重建，先显示上次的列表，不闪「加载中」。 */
let cachedChats: ChatSummary[] | null = null;

/** 按最后更新时间分组：今天 / 昨天 / 近 7 天 / 更早。 */
function groupChats(list: ChatSummary[]): { label: string; items: ChatSummary[] }[] {
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  const day = 86_400_000;
  const groups = [
    { label: "今天", from: start.getTime(), items: [] as ChatSummary[] },
    { label: "昨天", from: start.getTime() - day, items: [] as ChatSummary[] },
    { label: "近 7 天", from: start.getTime() - 6 * day, items: [] as ChatSummary[] },
    { label: "更早", from: -Infinity, items: [] as ChatSummary[] },
  ];
  for (const c of list) groups.find((g) => new Date(c.updated_at).getTime() >= g.from)!.items.push(c);
  return groups.filter((g) => g.items.length);
}

/** 列表里的时间：今天只写时分，今年写月-日，更早的带年份。 */
function chatTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const hm = d.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", hour12: false });
  if (d.toDateString() === now.toDateString()) return `今天 ${hm}`;
  const md = `${d.getMonth() + 1}-${d.getDate()}`;
  return d.getFullYear() === now.getFullYear() ? `${md} ${hm}` : `${d.getFullYear()}-${md}`;
}

/**
 * 问 AI：在正文里选中一段文字，旁边出一个「问 AI」按钮，点了在右侧打开对话面板，回答流式显示，可以追问。
 * 登录并且累计学习满 30 分钟才能用（后端 /ai/chat 也会检查）；没满时右下角入口照样显示，点了提示还差多久。
 */
export default function AskAI({ token, section }: { token: string; section: Section }) {
  const [access, setAccess] = useState<Access | null>(() => (unlockedTokens.has(token) ? UNLOCKED : null));
  const [lockTip, setLockTip] = useState(false); // 没解锁时点入口：弹出「还差多久」
  const isAdmin = !!access?.unlocked; // 下面沿用这个名字：能用问 AI
  const [open, setOpen] = useState(() => pendingChat !== null);
  const [closing, setClosing] = useState(false); // 正在播放滑出动画，播完再真正关掉
  const [quote, setQuote] = useState(() => pendingChat?.quote ?? "");
  const [chatId, setChatId] = useState<number | null>(() => pendingChat?.id ?? null); // 这次对话在后端的 id：第一次回答时后端发回来，追问时带上
  const [view, setView] = useState<"chat" | "history">("chat");
  const [chats, setChats] = useState<ChatSummary[] | null>(() => cachedChats);
  // 从别的节点点了一条历史对话、跳过来重新打开面板时，不再播放一遍滑入动画
  const [instant, setInstant] = useState(() => pendingChat !== null);
  const [historyErr, setHistoryErr] = useState("");
  const [sideOpen, setSideOpen] = useState(() => {
    try {
      return localStorage.getItem(SIDE_KEY) !== "0";
    } catch {
      return true;
    }
  });
  const panelRef = useRef<HTMLElement | null>(null);
  const [panelW, setPanelW] = useState(0);
  const [msgs, setMsgs] = useState<Msg[]>(() => pendingChat?.messages ?? []);
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
    if (unlockedTokens.has(token)) return;
    fetchAccess(token)
      .then((a) => alive && setAccess(a))
      .catch(() => alive && setAccess(null));
    return () => {
      alive = false;
    };
  }, [token]);


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
        setInstant(false); // 下次正常打开时照常有滑入动画
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
    setChatId(null);
    setView("chat");
    setMsgs([]);
    setInput("");
    setOpen(true);
    setClosing(false);
    stickRef.current = true;
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

  // 快捷键 ⌘J / Ctrl+J：正文里选了文字就带上它开始问；没选的话，面板开着就关、关着就开
  const shortcutRef = useRef<() => void>(() => {});
  useEffect(() => {
    shortcutRef.current = () => {
      const picked = pickSelection();
      if (picked) {
        startWithSelection(picked); // 选了文字：不管面板开没开，都用这段开始新对话
        return;
      }
      if (open && !closing) close();
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

  // ---------- 历史对话列表（左侧 / 历史视图共用） ----------
  const loadChats = useCallback(() => {
    apiGet<ChatSummary[]>("/ai/chats", token)
      .then((list) => {
        cachedChats = list;
        setChats(list);
        setHistoryErr("");
      })
      .catch((e: Error) => setHistoryErr(e.message));
  }, [token]);

  // 面板多宽：拖宽 / 窗口变化都会变，宽的时候左边放对话列表
  useEffect(() => {
    const el = panelRef.current;
    if (!open || !el) return;
    const ro = new ResizeObserver(([entry]) => setPanelW(entry.contentRect.width));
    ro.observe(el);
    return () => ro.disconnect();
  }, [open]);
  const wide = panelW >= SIDE_MIN_PANEL;
  const showSide = open && wide && sideOpen;

  // 左侧列表一出来就取一次
  useEffect(() => {
    if (showSide) loadChats();
  }, [showSide, loadChats]);

  const toggleHistory = () => {
    if (wide) {
      // 宽：收起 / 展开左侧列表，记住选择
      const next = !sideOpen;
      setSideOpen(next);
      try {
        localStorage.setItem(SIDE_KEY, next ? "1" : "0");
      } catch {
        // 存不了就只在这次生效
      }
      return;
    }
    // 窄：整个面板在「对话」和「历史列表」之间切换
    if (view === "history") {
      setView("chat");
      return;
    }
    setView("history");
    loadChats();
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

      // 发给后端的历史：原样发，选中的内容单独放在 quote 里，后端拼进第一个问题，同时存进历史
      const payload = history.map((m) => ({ role: m.role, content: m.content }));
      const update = (patch: Partial<Msg>) =>
        setMsgs((list) => [...list.slice(0, -1), { ...list[list.length - 1], ...patch }]);

      const controller = new AbortController();
      abortRef.current = controller;
      let answer = "";
      try {
        const res = await fetch(`${apiBase()}/ai/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({
            chat_id: chatId,
            section_id: section.id,
            section_title: section.title,
            section_text: text,
            quote: quote || null,
            messages: payload,
          }),
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
            if (event === "chat") {
              setChatId(payload.id); // 后端已经存下这次对话：追问时带上 id，接着存在同一条里
            } else if (event === "delta") {
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
        loadChats(); // 刚问完的这条排到历史最前面
      }
    },
    [busy, chatId, loadChats, msgs, quote, section.id, section.title, text, token],
  );

  const newChat = () => {
    abortRef.current?.abort();
    setChatId(null); // 旧的那条已经存在后端了，在「历史」里能找到
    setView("chat");
    setMsgs([]);
    setInput("");
    inputRef.current?.focus();
  };

  // ---------- 历史对话 ----------

  // 打开一条历史对话：取回消息、选中的内容，接着追问就存回同一条
  const loadChat = useCallback(
    (id: number) => {
      apiGet<ChatDetail>(`/ai/chats/${id}`, token)
        .then((c) => {
          abortRef.current?.abort();
          setChatId(c.id);
          setQuote(c.quote ?? "");
          quoteRangeRef.current = null; // 历史里的选中内容不一定还在当前页面上，不能「回到原文」
          setMsgs(c.messages.map((m) => ({ role: m.role, content: m.content, stopped: m.stopped })));
          setInput("");
          setView("chat");
          stickRef.current = true;
        })
        .catch((e: Error) => setHistoryErr(e.message));
    },
    [token],
  );

  // 跳过来时已经用 pendingChat 初始化好了，用完清掉，免得下次换节又打开
  useEffect(() => {
    pendingChat = null;
  }, []);

  const openChat = (c: ChatSummary) => {
    if (c.section_id && c.section_id !== section.id) {
      // 别的节问的：回答要结合那一节的正文。先把对话取回来，再跳过去，新的面板直接带着内容出现
      apiGet<ChatDetail>(`/ai/chats/${c.id}`, token)
        .then((d) => {
          pendingChat = { ...d, messages: d.messages.map((m) => ({ role: m.role, content: m.content, stopped: m.stopped })) };
          location.hash = c.section_id;
        })
        .catch((e: Error) => setHistoryErr(e.message));
      return;
    }
    loadChat(c.id);
  };

  const removeChat = async (c: ChatSummary) => {
    const res = await fetch(`${apiBase()}/ai/chats/${c.id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } }).catch(() => null);
    if (!res?.ok) {
      setHistoryErr("删除失败，稍后再试");
      return;
    }
    setChats((list) => {
      const next = list?.filter((x) => x.id !== c.id) ?? null;
      cachedChats = next;
      return next;
    });
    if (c.id === chatId) {
      setChatId(null);
      setMsgs([]);
    }
  };

  // 没解锁：入口照样显示（知道有这个功能），点了重新查一次时长，够了就直接打开
  const tryUnlock = () => {
    if (lockTip) {
      setLockTip(false);
      return;
    }
    fetchAccess(token)
      .then((a) => {
        setAccess(a);
        if (a.unlocked) openPanel();
        else setLockTip(true);
      })
      .catch(() => setLockTip(true));
  };

  if (!access) return null;

  if (!access.unlocked) {
    const left = Math.max(1, Math.ceil((access.need - access.seconds) / 60));
    return (
      <>
        {lockTip && (
          <div className="ask-ai-lock" role="status">
            <b>累计学习满 {access.need / 60} 分钟解锁问 AI</b>
            <span>
              已学 {Math.floor(access.seconds / 60)} 分钟，还差 {left} 分钟
            </span>
            <small>学习时长每分钟同步一次，刚学的可能要等一会儿才算上。</small>
          </div>
        )}
        <button type="button" className="ask-ai-fab locked" onClick={tryUnlock} title="问 AI：累计学习满 30 分钟解锁" aria-label="问 AI（未解锁）">
          <Sparkle />
        </button>
      </>
    );
  }

  const last = msgs.length - 1;

  // 历史对话列表：宽的时候放在左侧，窄的时候点「历史」占满面板
  const chatList = (
    <div className="ask-ai-history">
      {historyErr && <p className="ask-ai-err">{historyErr}</p>}
      {!chats && !historyErr && <p className="ask-ai-empty-hint">加载中…</p>}
      {chats && !chats.length && <p className="ask-ai-empty-hint">问过的问题会自动存在这里。</p>}
      {chats &&
        groupChats(chats).map((g) => (
          <div key={g.label} className="ask-ai-group">
            <p className="ask-ai-group-label">{g.label}</p>
            <ul>
              {g.items.map((c) => (
                <li key={c.id} className={c.id === chatId ? "on" : ""}>
                  <button type="button" className="ask-ai-chat" onClick={() => openChat(c)} title={`${c.title}\n${c.section_title} · ${chatTime(c.updated_at)}`}>
                    <b>{c.title}</b>
                    <span>{c.section_id === section.id ? "本节" : c.section_title}</span>
                  </button>
                  <button type="button" className="ask-ai-del" onClick={() => void removeChat(c)} aria-label="删除这条对话" title="删除">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3" />
                    </svg>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
    </div>
  );

  return (
    <>

      {!open && (
        <button
          type="button"
          className="ask-ai-fab"
          onMouseDown={(e) => e.preventDefault()} // 点按钮时不把正文里选中的文字取消掉
          onClick={() => {
            // 划词时不再自动弹按钮（太打扰）：选中一段后点这里或按快捷键，就带上选中的内容
            const picked = pickSelection();
            if (picked) startWithSelection(picked);
            else openPanel();
          }}
          title={`问 AI（${SHORTCUT}）：问这一节的问题；先选中正文再点这里或按 ${SHORTCUT}，会针对选中的内容回答`}
          aria-label="问 AI"
        >
          <Sparkle />
        </button>
      )}

      {open && <div className={`ask-ai-mask ${closing ? "closing" : ""} ${instant ? "instant" : ""}`} onClick={close} aria-hidden="true" />}

      {open && (
        <section
          ref={panelRef}
          className={`ask-ai ${closing ? "closing" : ""} ${instant ? "instant" : ""}`}
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
            <button
              type="button"
              className={`ask-ai-new ${(wide ? showSide : view === "history") ? "on" : ""}`}
              onClick={toggleHistory}
              title={wide ? "收起 / 展开左边的历史对话" : "以前问过的对话"}
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5M12 7v5l3 2" />
              </svg>
              历史
            </button>
            {!showSide && (msgs.length > 0 || (!wide && view === "history")) && (
              <button type="button" className="ask-ai-new" onClick={newChat} title="开始一次新对话；当前对话已经自动存进「历史」">
                {/* 写成文字按钮：之前只放一个铅笔图标，看着像「编辑」，其实是清空重来 */}
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                  <path d="M12 5v14M5 12h14" />
                </svg>
                新对话
              </button>
            )}
            <button type="button" className="ask-ai-icon" onClick={close} aria-label="关闭（Esc）" title="关闭（Esc）">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                <path d="M6 6l12 12M18 6 6 18" />
              </svg>
            </button>
          </header>

          <div className="ask-ai-row">
            {showSide && (
              <nav className="ask-ai-side" aria-label="历史对话">
                <button type="button" className="ask-ai-side-new" onClick={newChat}>
                  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                  新对话
                </button>
                {chatList}
              </nav>
            )}
            <div className="ask-ai-col">
              {!wide && view === "history" && chatList}


          <div
            className="ask-ai-list"
            hidden={!wide && view === "history"}
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
                    直接问这一节的问题；也可以先在正文里选中一段，再点右下角的按钮或按 {SHORTCUT}，回答会针对那一段。
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
            hidden={!wide && view === "history"}
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
            </div>
          </div>
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
