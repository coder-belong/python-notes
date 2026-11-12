"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import type { Notes, Section } from "@/lib/notes";
import { SIDE_COLLAPSED_KEY } from "@/lib/prefs";
import { dayKey, formatDuration, loadReading, saveReading, type Reading } from "@/lib/study-store";
import { useStudy } from "@/lib/use-study";

import AccountPanel, { AccountEntry } from "./AccountPanel";
import ChangelogPanel from "./ChangelogPanel";
import FocusBar from "./FocusBar";
import Home from "./Home";
import MoreMenu from "./MoreMenu";
import SideResizer from "./SideResizer";
import ThemeToggle from "./ThemeToggle";
import StudyPanel, { StudyEntry } from "./StudyPanel";

/** 看过的最新一条更新日志的日期：比它新的就在「⋯」上显示小红点。 */
const CHANGELOG_SEEN_KEY = "python-notes:changelog-seen";

/** 第 0 节没有所属部分，侧栏里归到这一组。 */
const NO_PART = "开始之前";

export type Group = { part: string; items: Section[] };

/**
 * 页面一次只显示一节：网址 #节的id 就是那一节，没有 # 就是首页。
 * 用 # 而不是真的分页，是为了打包成单个 HTML 后，双击打开照样能切换。
 */
export default function NotesApp({ notes }: { notes: Notes }) {
  const { sections } = notes;
  // undefined：还没读到网址（服务端预渲染和刚打开的一瞬间）；null：首页
  const [route, setRoute] = useState<string | null | undefined>(undefined);
  const [navOpen, setNavOpen] = useState(false);
  const [statsOpen, setStatsOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [changelogOpen, setChangelogOpen] = useState(false);
  const [changelogSeen, setChangelogSeen] = useState<string | null>(null);
  // 侧栏收成窄条：<head> 里的脚本已经按上次的状态加好了 class，这里读出来让按钮显示对
  const [collapsed, setCollapsed] = useState(false);
  const [focus, setFocus] = useState(false);
  const [openParts, setOpenParts] = useState<Set<string>>(new Set());
  const [reading, setReading] = useState<Reading | null>(null);
  const restoreY = useRef<number | null>(null);
  const study = useStudy(route ?? null);

  const index = route ? sections.findIndex((s) => s.id === route) : -1;
  const section = index >= 0 ? sections[index] : null;
  const prev = index > 0 ? sections[index - 1] : null;
  const next = index >= 0 && index < sections.length - 1 ? sections[index + 1] : null;

  // 按「部分」分组，给侧栏和首页用
  const groups = useMemo(() => {
    const out: Group[] = [];
    for (const s of sections) {
      const part = s.part ?? NO_PART;
      const last = out[out.length - 1];
      if (last && last.part === part) last.items.push(s);
      else out.push({ part, items: [s] });
    }
    return out;
  }, [sections]);

  // 网址 # 变了就切到对应的节；回到上次读的那一节时恢复滚动位置
  useEffect(() => {
    const saved = loadReading();
    // 只能在浏览器里读 localStorage 和网址，读完同步到 state
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setReading(saved);
    const apply = () => {
      const id = decodeURIComponent(location.hash.slice(1));
      const found = sections.some((s) => s.id === id);
      const last = loadReading();
      restoreY.current = found && last?.id === id ? last.y : null;
      setRoute(found ? id : null);
      setNavOpen(false);
    };
    apply();
    window.addEventListener("hashchange", apply);
    return () => window.removeEventListener("hashchange", apply);
  }, [sections]);

  // 切节后：回到顶部（或上次的位置）、展开所在的部分
  useEffect(() => {
    if (route === undefined) return;
    window.scrollTo({ top: restoreY.current ?? 0, behavior: "instant" });
    restoreY.current = null;
    if (section) {
      const part = section.part ?? NO_PART;
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setOpenParts((s) => (s.has(part) ? s : new Set(s).add(part)));
    }
  }, [route, section]);

  // 记住读到哪：停止滚动半秒后存一次
  useEffect(() => {
    if (!route) return;
    let timer = 0;
    const save = () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        const r = { id: route, y: Math.round(window.scrollY) };
        saveReading(r);
        setReading(r);
      }, 500);
    };
    save();
    window.addEventListener("scroll", save, { passive: true });
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("scroll", save);
    };
  }, [route]);

  // 读上次的侧栏状态、看过的最新一条更新日志
  useEffect(() => {
    // 只能在浏览器里读，读完同步到 state
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setCollapsed(document.documentElement.classList.contains("side-collapsed"));
    try {
      setChangelogSeen(localStorage.getItem(CHANGELOG_SEEN_KEY) ?? "");
    } catch {
      setChangelogSeen("");
    }
  }, []);

  const toggleSidebar = () =>
    setCollapsed((v) => {
      const next = !v;
      document.documentElement.classList.toggle("side-collapsed", next);
      try {
        localStorage.setItem(SIDE_COLLAPSED_KEY, next ? "1" : "0");
      } catch {
        // 存不了就只在这次有效
      }
      return next;
    });

  const latestChange = notes.changelog[0]?.date ?? "";
  // 还没读到 localStorage 时先不显示红点，免得一闪
  const hasNewChange = changelogSeen !== null && latestChange > changelogSeen;
  const openChangelog = () => {
    setChangelogOpen(true);
    setChangelogSeen(latestChange);
    try {
      localStorage.setItem(CHANGELOG_SEEN_KEY, latestChange);
    } catch {
      // 存不了下次还会显示红点，不影响使用
    }
  };

  // 键盘：← → 切换上一节 / 下一节（在输入框里、或者开着弹窗时不响应）
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (statsOpen || accountOpen || changelogOpen || e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) return;
      if ((e.target as HTMLElement).closest?.("input, textarea, [contenteditable]")) return;
      // \ 收起 / 展开侧栏
      if (e.key === "\\") {
        toggleSidebar();
        return;
      }
      // F 进入 / 退出专注模式，Esc 退出
      if (e.key === "f" || e.key === "F") {
        setFocus((v) => !v);
        return;
      }
      if (e.key === "Escape") {
        setFocus(false);
        return;
      }
      const to = e.key === "ArrowLeft" ? prev : e.key === "ArrowRight" ? next : null;
      if (to) location.hash = to.id;
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [prev, next, statsOpen, accountOpen, changelogOpen]);

  // 专注模式：给 <html> 加个 class，CSS 负责收起侧栏、正文居中
  useEffect(() => {
    document.documentElement.classList.toggle("focus-mode", focus);
  }, [focus]);

  // 给代码块加「复制」按钮（每次换节，正文换了就重新加）
  useEffect(() => {
    const buttons: HTMLButtonElement[] = [];
    document.querySelectorAll<HTMLPreElement>(".content pre").forEach((pre) => {
      const code = pre.querySelector("code");
      if (!code) return;
      const btn = document.createElement("button");
      btn.className = "copy";
      btn.type = "button";
      btn.textContent = "复制";
      btn.onclick = () => {
        navigator.clipboard.writeText(code.innerText).then(() => {
          btn.textContent = "已复制";
          window.setTimeout(() => (btn.textContent = "复制"), 1200);
        });
      };
      pre.appendChild(btn);
      buttons.push(btn);
    });
    return () => buttons.forEach((b) => b.remove());
  }, [route]);

  const togglePart = (part: string) =>
    setOpenParts((s) => {
      const n = new Set(s);
      if (n.has(part)) n.delete(part);
      else n.add(part);
      return n;
    });

  const doneThenNext = () => {
    if (!section) return;
    if (!study.data.done[section.id]) study.toggleDone(section.id);
    if (next) location.hash = next.id;
  };

  return (
    <>
      {/* 标签页标题跟着当前节变；React 会把它放进 <head> */}
      <title>{section ? `${section.title} · ${notes.title}` : notes.title}</title>
      <button className="menu-btn" type="button" onClick={() => setNavOpen((v) => !v)}>
        目录
      </button>

      <aside className={navOpen ? "open" : ""}>
        {/* 收起后的窄条：只留常用按钮（只在宽屏显示，窄屏侧栏是抽屉，不收窄条） */}
        <div className="side-rail">
          <button
            type="button"
            className="icon-btn"
            onClick={toggleSidebar}
            aria-label="展开侧栏"
            title="展开侧栏（\）"
          >
            <SidebarIcon />
          </button>
          <button
            type="button"
            className={`icon-btn rail-study ${study.status}`}
            onClick={() => setStatsOpen(true)}
            aria-label="学习统计"
            title={`今天 ${formatDuration(study.data.days[dayKey()] ?? 0)} · 学习统计`}
          >
            <span className="pulse" />
          </button>
          <span className="rail-gap" />
          <MoreMenu
            hasNew={hasNewChange}
            onOpenChangelog={openChangelog}
            collapsed={collapsed}
            onToggleSidebar={toggleSidebar}
            placement="right"
          />
          <AccountEntry study={study} onOpen={() => setAccountOpen(true)} />
          <ThemeToggle />
        </div>

        <div className="side-full">
          <div className="brand-row">
            <button
              type="button"
              className="icon-btn side-toggle"
              onClick={toggleSidebar}
              aria-label="收起侧栏"
              title="收起侧栏（\）"
            >
              <SidebarIcon />
            </button>
            <a className="brand" href="#">
              {notes.title}
            </a>
            <MoreMenu
              hasNew={hasNewChange}
              onOpenChangelog={openChangelog}
              collapsed={collapsed}
              onToggleSidebar={toggleSidebar}
              placement="down"
            />
            <AccountEntry study={study} onOpen={() => setAccountOpen(true)} />
            <ThemeToggle />
          </div>
          <StudyEntry study={study} onOpen={() => setStatsOpen(true)} />
          <nav>
            <a href="#" className={`nav-home ${route === null ? "active" : ""}`}>
              首页 · 学习路线
            </a>
            {groups.map((g) => {
              const done = g.items.filter((s) => study.data.done[s.id]).length;
              const open = openParts.has(g.part);
              return (
                <div key={g.part} className="nav-group">
                  <button type="button" className="nav-part" onClick={() => togglePart(g.part)} aria-expanded={open}>
                    <span className={`chev ${open ? "open" : ""}`}>›</span>
                    <span className="nav-part-name" title={g.part}>
                      {g.part}
                    </span>
                    <span className="nav-part-count">
                      {done}/{g.items.length}
                    </span>
                    <span className="mini-bar">
                      <i style={{ width: `${(done / g.items.length) * 100}%` }} />
                    </span>
                  </button>
                  {open &&
                    g.items.map((s) => {
                      const cls = ["nav-sec", route === s.id ? "active" : "", study.data.done[s.id] ? "done" : ""]
                        .filter(Boolean)
                        .join(" ");
                      return (
                        <a key={s.id} href={`#${s.id}`} className={cls} title={s.title}>
                          <span className="dot" />
                          {s.num && <span className="sec-num">{s.num}</span>}
                          <span className="nav-name">{s.name}</span>
                        </a>
                      );
                    })}
                </div>
              );
            })}
          </nav>
        </div>
      </aside>
      <SideResizer />

      <main>
        <div className="content">
          {route === null && (
            <Home notes={notes} groups={groups} done={study.data.done} reading={reading} studyDays={study.data.days} />
          )}

          {section && (
            <article key={section.id}>
              <div className="crumb">
                <a href="#">首页</a>
                <span>/</span>
                <span>{section.part ?? NO_PART}</span>
                <span className="crumb-count">
                  第 {index + 1} / {sections.length} 节
                </span>
                {!focus && (
                  <button type="button" className="focus-btn" onClick={() => setFocus(true)} title="专注模式（F）">
                    <FocusIcon />
                    专注
                  </button>
                )}
              </div>
              {section.partIntroHtml && (
                <div className="part-intro" dangerouslySetInnerHTML={{ __html: section.partIntroHtml }} />
              )}
              <h2 id={section.id} className="page-title">
                <span>{section.title}</span>
                <span className="sec-meta">
                  <label className="done-toggle">
                    <input
                      type="checkbox"
                      checked={!!study.data.done[section.id]}
                      onChange={() => study.toggleDone(section.id)}
                    />
                    学完了
                  </label>
                </span>
              </h2>
              <div dangerouslySetInnerHTML={{ __html: section.html }} />

              <div className="finish">
                <button type="button" className="finish-btn" onClick={doneThenNext}>
                  {study.data.done[section.id]
                    ? next
                      ? "下一节 →"
                      : "已全部学完 🎉"
                    : next
                      ? "学完了，下一节 →"
                      : "学完了 🎉"}
                </button>
              </div>

              <nav className="pager">
                {prev ? (
                  <a href={`#${prev.id}`} className="pager-prev">
                    <span>← 上一节</span>
                    <b>{prev.title}</b>
                  </a>
                ) : (
                  <a href="#" className="pager-prev">
                    <span>← 回到</span>
                    <b>首页</b>
                  </a>
                )}
                {next && (
                  <a href={`#${next.id}`} className="pager-next">
                    <span>下一节 →</span>
                    <b>{next.title}</b>
                  </a>
                )}
              </nav>
              <p className="hint pager-hint">键盘 ← → 切换上一节 / 下一节，F 进入专注模式</p>
            </article>
          )}
        </div>
      </main>

      {focus && (
        <FocusBar
          today={study.data.pomodoros[dayKey()] ?? 0}
          onComplete={study.addPomodoro}
          onExit={() => setFocus(false)}
        />
      )}
      {statsOpen && <StudyPanel study={study} sections={sections} onClose={() => setStatsOpen(false)} />}
      {accountOpen && <AccountPanel study={study} onClose={() => setAccountOpen(false)} />}
      {changelogOpen && <ChangelogPanel days={notes.changelog} onClose={() => setChangelogOpen(false)} />}
    </>
  );
}

/** 侧栏开关的图标：一个方框，左边一竖。 */
function SidebarIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="18"
      height="18"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      aria-hidden="true"
    >
      <rect x="3.5" y="4.5" width="17" height="15" rx="2.5" />
      <path d="M9.5 4.5v15" />
    </svg>
  );
}

function FocusIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="14"
      height="14"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <path d="M4 9V5a1 1 0 0 1 1-1h4M15 4h4a1 1 0 0 1 1 1v4M20 15v4a1 1 0 0 1-1 1h-4M9 20H5a1 1 0 0 1-1-1v-4" />
      <circle cx="12" cy="12" r="2.5" />
    </svg>
  );
}
