"use client";

import { useEffect } from "react";

import type { ChangelogDay } from "@/lib/notes";
import { dayKey } from "@/lib/study-store";
import { blurActive } from "@/lib/blur";

import "./ChangelogPanel.css";

/** 每种更新类型一个颜色；同一天里按这个顺序排：新功能在最上面，笔记在最下面。 */
const TAGS = ["新功能", "改进", "修复", "笔记"] as const;
const TAG_CLASS: Record<string, string> = { 新功能: "feat", 改进: "improve", 修复: "fix", 笔记: "notes" };

/** 2026-11-12 → { day: "11 月 12 日", rel: "今天" }。 */
function dateParts(date: string): { day: string; rel: string } {
  const d = new Date(`${date}T00:00:00`);
  if (Number.isNaN(d.getTime())) return { day: date, rel: "" };
  const now = new Date();
  const yesterday = dayKey(new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1));
  const rel = date === dayKey(now) ? "今天" : date === yesterday ? "昨天" : "";
  const year = d.getFullYear() === now.getFullYear() ? "" : `${d.getFullYear()} 年 `;
  return { day: `${year}${d.getMonth() + 1} 月 ${d.getDate()} 日`, rel };
}

const order = (tag: string | null) => (tag ? TAGS.indexOf(tag as (typeof TAGS)[number]) : TAGS.length);

/** 更新日志弹窗：按日期分组（日期滚动时吸顶），每条前面一个类型标签。内容来自 content/changelog.md。 */
export default function ChangelogPanel({ days, onClose }: { days: ChangelogDay[]; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      blurActive(); // 不然打开弹窗的那个按钮会留下一圈焦点框
      onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop pinned" onClick={onClose}>
      <div className="modal cl-modal" role="dialog" aria-label="更新日志" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head cl-head">
          <h3>更新日志</h3>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>

        <div className="cl-body">
          {days.map((day) => {
            const { day: label, rel } = dateParts(day.date);
            const entries = [...day.entries].sort((a, b) => order(a.tag) - order(b.tag)); // sort 是稳定的：同类型保持原来的顺序
            return (
              <section key={day.date} className="cl-day">
                <h4 className="cl-date">
                  {label}
                  {rel && <span>{rel}</span>}
                </h4>
                <ul>
                  {entries.map((e, j) => (
                    <li key={j}>
                      <span className={`cl-tag ${e.tag ? (TAG_CLASS[e.tag] ?? "") : ""}`}>{e.tag ?? "其他"}</span>
                      <span className="cl-text" dangerouslySetInnerHTML={{ __html: e.html }} />
                    </li>
                  ))}
                </ul>
              </section>
            );
          })}
        </div>
      </div>
    </div>
  );
}
