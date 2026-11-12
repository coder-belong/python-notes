"use client";

import { useEffect } from "react";

import type { ChangelogDay, ChangelogEntry } from "@/lib/notes";
import { dayKey } from "@/lib/study-store";

/** 分组顺序和每组的图标（参考 Ant Design 更新日志的写法）。 */
const GROUPS = [
  { tag: "新功能", icon: "🆕" },
  { tag: "改进", icon: "💄" },
  { tag: "笔记", icon: "📝" },
  { tag: "修复", icon: "🐞" },
] as const;

/** 2026-11-12 → 「今天」「昨天」，更早的不写。 */
function relDay(date: string): string {
  const now = new Date();
  if (date === dayKey(now)) return "今天";
  if (date === dayKey(new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1))) return "昨天";
  return "";
}

function Entries({ entries }: { entries: ChangelogEntry[] }) {
  return (
    <ul>
      {entries.map((e, i) => (
        <li key={i}>
          {e.title && <b dangerouslySetInnerHTML={{ __html: e.title }} />}
          <span dangerouslySetInnerHTML={{ __html: e.html }} />
        </li>
      ))}
    </ul>
  );
}

/** 更新日志弹窗：一个版本一块，版本号 + 日期 + 一句话概要，下面按「新功能 / 改进 / 笔记 / 修复」分组。 */
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
          <div>
            <h3>更新日志</h3>
            <p className="changelog-sub">每个版本改了什么，最新的在最上面</p>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>

        <div className="changelog">
          {days.map((day, i) => {
            const rel = relDay(day.date);
            const known = new Set<string>(GROUPS.map((g) => g.tag));
            const other = day.entries.filter((e) => !e.tag || !known.has(e.tag));
            return (
              <section key={`${day.version}-${day.date}`} className="changelog-version">
                <header>
                  {day.version && <h4>{day.version}</h4>}
                  <time dateTime={day.date}>
                    {day.date}
                    {rel && ` · ${rel}`}
                  </time>
                  {i === 0 && <span className="changelog-latest">最新</span>}
                </header>
                {day.summaryHtml && (
                  <p className="changelog-summary" dangerouslySetInnerHTML={{ __html: day.summaryHtml }} />
                )}
                {GROUPS.map((g) => {
                  const entries = day.entries.filter((e) => e.tag === g.tag);
                  if (entries.length === 0) return null;
                  return (
                    <div key={g.tag} className="changelog-group">
                      <h5>
                        <span aria-hidden="true">{g.icon}</span>
                        {g.tag}
                      </h5>
                      <Entries entries={entries} />
                    </div>
                  );
                })}
                {other.length > 0 && (
                  <div className="changelog-group">
                    <h5>其他</h5>
                    <Entries entries={other} />
                  </div>
                )}
              </section>
            );
          })}
        </div>
      </div>
    </div>
  );
}
