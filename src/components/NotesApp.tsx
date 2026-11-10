"use client";

import { useEffect, useMemo, useState } from "react";

import type { Notes } from "@/lib/notes";
import { useStudy } from "@/lib/use-study";

import StudyPanel, { StudyEntry } from "./StudyPanel";

export default function NotesApp({ notes }: { notes: Notes }) {
  const { sections } = notes;
  const [current, setCurrent] = useState<string | null>(sections[0]?.id ?? null);
  const [navOpen, setNavOpen] = useState(false);
  const [statsOpen, setStatsOpen] = useState(false);
  const study = useStudy(current);

  // 按「部分」分组，给侧边目录用
  const groups = useMemo(() => {
    const out: { part: string | null; items: typeof sections }[] = [];
    for (const s of sections) {
      const last = out[out.length - 1];
      if (last && last.part === s.part) last.items.push(s);
      else out.push({ part: s.part, items: [s] });
    }
    return out;
  }, [sections]);

  // 滚动时算出当前读到哪一节：标题滚过屏幕上方 120px 的最后一节
  useEffect(() => {
    const heads = sections
      .map((s) => document.getElementById(s.id))
      .filter((el): el is HTMLElement => el !== null);
    const onScroll = () => {
      let id = heads[0]?.id ?? null;
      for (const h of heads) if (h.getBoundingClientRect().top < 120) id = h.id;
      setCurrent(id);
    };
    onScroll();
    document.addEventListener("scroll", onScroll, { passive: true });
    return () => document.removeEventListener("scroll", onScroll);
  }, [sections]);

  // 给每个代码块加「复制」按钮
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
  }, []);

  return (
    <>
      <button className="menu-btn" type="button" onClick={() => setNavOpen((v) => !v)}>
        目录
      </button>

      <aside className={navOpen ? "open" : ""}>
        <div className="brand">{notes.title}</div>
        <StudyEntry study={study} onOpen={() => setStatsOpen(true)} />
        <nav>
          {groups.map((g, i) => (
            <div key={i}>
              {g.part && <div className="nav-part">{g.part}</div>}
              {g.items.map((s) => {
                const cls = ["nav-sec", current === s.id ? "active" : "", study.data.done[s.id] ? "done" : ""]
                  .filter(Boolean)
                  .join(" ");
                return (
                  <a key={s.id} href={`#${s.id}`} className={cls} onClick={() => setNavOpen(false)}>
                    <span className="dot" />
                    <span className="nav-name">{s.title}</span>
                  </a>
                );
              })}
            </div>
          ))}
        </nav>
      </aside>

      <main>
        <div className="content">
          <header className="top">
            <h1>{notes.title}</h1>
            <div dangerouslySetInnerHTML={{ __html: notes.introHtml }} />
          </header>

          {sections.map((s, i) => {
            const startsPart = s.part && s.part !== sections[i - 1]?.part;
            return (
              <section key={s.id}>
                {startsPart && <h1 className="part-title">{s.part}</h1>}
                {s.partIntroHtml && <div className="part-intro" dangerouslySetInnerHTML={{ __html: s.partIntroHtml }} />}
                <h2 id={s.id}>
                  <span>{s.title}</span>
                  <span className="sec-meta">
                    <label className="done-toggle">
                      <input
                        type="checkbox"
                        checked={!!study.data.done[s.id]}
                        onChange={() => study.toggleDone(s.id)}
                      />
                      学完了
                    </label>
                  </span>
                </h2>
                <div dangerouslySetInnerHTML={{ __html: s.html }} />
              </section>
            );
          })}
        </div>
      </main>

      {statsOpen && <StudyPanel study={study} sections={sections} onClose={() => setStatsOpen(false)} />}
    </>
  );
}
