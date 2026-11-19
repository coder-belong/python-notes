/**
 * 学习过程：从每节的开始日期（started）、学完日期（finished）算出按天的时间线。
 * 只做计算，不存东西；日期都是本地日期字符串 2026-11-18。
 */

import type { Section } from "./notes";
import type { StudyData } from "./study-store";

export type ProgressEvent = {
  day: string;
  kind: "stage-done" | "done" | "start" | "stage-start";
  text: string;
  href: string;
};

/** 排序：同一天里「学完阶段」在最上，然后学完的节、开始的节、开始的阶段。 */
const ORDER: Record<ProgressEvent["kind"], number> = { "stage-done": 0, done: 1, start: 2, "stage-start": 3 };

/**
 * 一个阶段哪天开始、哪天学完。
 * 开始：开始学或学完的日期里最早的（有的节可能只记了学完）。
 * 学完：每节都勾了学完、并且都有日期时，取最后学完的那天；有节没记日期就算不出来。
 */
function stageDates(items: Section[], data: StudyData): { startedOn: string | null; finishedOn: string | null } {
  const starts = items.flatMap((s) => [data.started[s.id], data.finished[s.id]]).filter(Boolean).sort();
  const allDone = items.every((s) => data.done[s.id]);
  const finishes = items.map((s) => data.finished[s.id]);
  const allDated = finishes.every(Boolean);
  return {
    startedOn: starts[0] ?? null,
    finishedOn: allDone && allDated ? finishes.sort().at(-1)! : null,
  };
}

/** 所有「开始学 / 学完」的事件，新的在前。 */
export function progressEvents(groups: { part: string; items: Section[] }[], data: StudyData): ProgressEvent[] {
  const out: ProgressEvent[] = [];
  for (const g of groups) {
    for (const s of g.items) {
      if (data.started[s.id]) out.push({ day: data.started[s.id], kind: "start", text: s.title, href: `#${s.id}` });
      if (data.done[s.id] && data.finished[s.id])
        out.push({ day: data.finished[s.id], kind: "done", text: s.title, href: `#${s.id}` });
    }
    // 只给有编号的「阶段」记阶段事件，「开始之前」这种不算
    if (!g.items.some((s) => s.num)) continue;
    const { startedOn, finishedOn } = stageDates(g.items, data);
    const href = `#${(g.items.find((s) => !data.done[s.id]) ?? g.items[0]).id}`;
    if (startedOn) out.push({ day: startedOn, kind: "stage-start", text: g.part, href });
    if (finishedOn) out.push({ day: finishedOn, kind: "stage-done", text: g.part, href });
  }
  return out.sort((a, b) => b.day.localeCompare(a.day) || ORDER[a.kind] - ORDER[b.kind]);
}

/** 2026-11-18 → 「11月18日 周三」；不是今年的带上年份。 */
export function formatDayWithWeek(day: string): string {
  const [y, m, d] = day.split("-").map(Number);
  const w = "日一二三四五六"[new Date(`${day}T00:00:00`).getDay()];
  const md = `${m}月${d}日 周${w}`;
  return y === new Date().getFullYear() ? md : `${y}年${md}`;
}
