"use client";

import { useEffect } from "react";

import type { ChangelogDay } from "@/lib/notes";
import { dayKey } from "@/lib/study-store";

/** 每种更新类型一个颜色。 */
const TAG_CLASS: Record<string, string> = {
  新功能: "feat",
  改进: "improve",
  笔记: "notes",
  修复: "fix",
};

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

/** 更新日志弹窗：左边日期，右边一句一条；类型用小圆点颜色区分。内容来自 content/changelog.md。 */
export default function ChangelogPanel({ days, onClose }: { days: ChangelogDay[]; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop pinned" onClick={onClose}>
      <div className="modal changelog-modal" role="dialog" aria-label="更新日志" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>更新日志</h3>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>
        <div className="changelog-legend">
          {Object.entries(TAG_CLASS)
            .filter(([name]) => days.some((d) => d.entries.some((e) => e.tag === name)))
            .map(([name, cls]) => (
              <span key={name}>
                <i className={cls} />
                {name}
              </span>
            ))}
        </div>

        <div className="changelog">
          {days.map((day) => {
            const { day: label, rel } = dateParts(day.date);
            return (
              <section key={day.date} className="changelog-day">
                <div className="changelog-date">
                  <b>{label}</b>
                  {rel && <span>{rel}</span>}
                </div>
                <ul>
                  {day.entries.map((e, j) => (
                    <li key={j} title={e.tag ?? undefined}>
                      <i className={e.tag ? (TAG_CLASS[e.tag] ?? "") : ""} />
                      <span dangerouslySetInnerHTML={{ __html: e.html }} />
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
