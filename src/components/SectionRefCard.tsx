"use client";

import { useEffect, useRef, useState } from "react";

import type { Section } from "@/lib/notes";

import "./SectionRefCard.css";

type Card = { section: Section; x: number; y: number; above: boolean; pinned: boolean };

const CARD_W = 320;
const OPEN_DELAY = 250; // 鼠标停一会儿才出卡片，划过去不打扰
const CLOSE_DELAY = 180; // 离开后稍等再关：给鼠标从链接挪到卡片上的时间

/**
 * 正文里的「4.2 节」这类引用：悬停或点击时弹出一张小卡片（哪一节、讲什么、小标题、学完没有），
 * 卡片里点「跳到这一节」才真的跳。链接是 notes.ts 生成的 a.sec-ref；导读页里写成链接的节号也一样处理。
 */
export default function SectionRefCard({ sections, done }: { sections: Section[]; done: Record<string, boolean> }) {
  const [card, setCard] = useState<Card | null>(null);
  const openTimer = useRef(0);
  const closeTimer = useRef(0);
  const cardRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const byId = new Map(sections.map((s) => [s.id, s]));
    // 找到这次鼠标 / 点击落在的引用链接，以及它指向的那一节
    const refOf = (target: EventTarget | null) => {
      // 只管正文里的链接：上一节 / 下一节、首页这些照常跳转
      const a = (target as Element | null)?.closest?.(".sec-html a[href^='#']") as HTMLAnchorElement | null;
      if (!a || a.closest(".sec-card")) return null;
      const section = byId.get(decodeURIComponent(a.getAttribute("href")!.slice(1)));
      return section ? { a, section } : null;
    };
    const place = (a: HTMLElement, section: Section, pinned: boolean): Card => {
      const r = a.getBoundingClientRect();
      const x = Math.min(Math.max(r.left + r.width / 2 - CARD_W / 2, 12), window.innerWidth - CARD_W - 12);
      const above = r.bottom + 230 > window.innerHeight && r.top > 240; // 下面放不下就放上面
      return { section, x, y: above ? r.top - 8 : r.bottom + 8, above, pinned };
    };

    const onOver = (e: MouseEvent) => {
      const ref = refOf(e.target);
      if (!ref) return;
      window.clearTimeout(closeTimer.current);
      window.clearTimeout(openTimer.current);
      openTimer.current = window.setTimeout(
        () => setCard((c) => (c?.pinned ? c : place(ref.a, ref.section, false))),
        OPEN_DELAY,
      );
    };
    const onOut = (e: MouseEvent) => {
      if (!refOf(e.target)) return;
      window.clearTimeout(openTimer.current);
      closeTimer.current = window.setTimeout(() => setCard((c) => (c?.pinned ? c : null)), CLOSE_DELAY);
    };
    const onClick = (e: MouseEvent) => {
      const ref = refOf(e.target);
      if (ref) {
        // 点引用不直接跳：固定显示卡片（手机上没有悬停，只能靠点）；再点一次同一个就收起
        e.preventDefault();
        window.clearTimeout(openTimer.current);
        setCard((c) => (c?.pinned && c.section.id === ref.section.id ? null : place(ref.a, ref.section, true)));
        return;
      }
      if (!cardRef.current?.contains(e.target as Node)) setCard(null); // 点到别处就关
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setCard(null);
    const onScroll = () => setCard(null); // 卡片是固定定位的，页面一滚就对不上了

    document.addEventListener("mouseover", onOver);
    document.addEventListener("mouseout", onOut);
    document.addEventListener("click", onClick);
    window.addEventListener("keydown", onKey);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("hashchange", onScroll);
    return () => {
      window.clearTimeout(openTimer.current);
      window.clearTimeout(closeTimer.current);
      document.removeEventListener("mouseover", onOver);
      document.removeEventListener("mouseout", onOut);
      document.removeEventListener("click", onClick);
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("hashchange", onScroll);
    };
  }, [sections]);

  if (!card) return null;
  const { section: s } = card;
  const learned = !!done[s.id];

  return (
    <div
      ref={cardRef}
      className={`sec-card ${card.above ? "above" : ""}`}
      style={{ left: card.x, top: card.y, width: CARD_W }}
      role="dialog"
      aria-label={s.title}
      onMouseEnter={() => window.clearTimeout(closeTimer.current)}
      onMouseLeave={() => {
        if (!card.pinned) closeTimer.current = window.setTimeout(() => setCard(null), CLOSE_DELAY);
      }}
    >
      <p className="sec-card-part">{s.part}</p>
      <p className="sec-card-title">
        {s.num && <span>{s.num}</span>}
        {s.name}
      </p>
      {s.summary && <p className="sec-card-sum">{s.summary}</p>}
      {s.toc.length > 0 && (
        <ul className="sec-card-toc">
          {s.toc.slice(0, 4).map((t) => (
            <li key={t.id}>{t.text}</li>
          ))}
          {s.toc.length > 4 && <li className="more">还有 {s.toc.length - 4} 个小标题</li>}
        </ul>
      )}
      <div className="sec-card-foot">
        <span className={learned ? "learned" : ""}>{learned ? "✓ 已学完" : s.guide ? "阶段导读" : "还没学"}</span>
        <a href={`#${s.id}`} onClick={() => setCard(null)}>
          跳到这一节 →
        </a>
      </div>
    </div>
  );
}
