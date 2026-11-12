"use client";

import { useEffect, useRef } from "react";

import { dayKey, formatDuration } from "@/lib/study-store";

/** 每天学了多久 → 颜色深浅 0~4 档。 */
function level(seconds: number): number {
  if (seconds < 60) return 0;
  if (seconds < 15 * 60) return 1;
  if (seconds < 30 * 60) return 2;
  if (seconds < 60 * 60) return 3;
  return 4;
}

const ROW_LABELS = ["一", "", "三", "", "五", "", "日"];

type Props = {
  days: Record<string, number>;
  /** 显示最近多少周（最后一列是本周）。 */
  weeks?: number;
};

/** 学习热力图：一格一天，一列一周（周一在上），颜色越深学得越久。 */
export default function Heatmap({ days, weeks = 53 }: Props) {
  const scroller = useRef<HTMLDivElement>(null);

  // 放不下时可以横向滚动，默认滚到最右边（最近的日子）
  useEffect(() => {
    // 等格子按宽度排好再滚，否则量到的宽度还不对
    const id = requestAnimationFrame(() => {
      const el = scroller.current;
      if (el) el.scrollLeft = el.scrollWidth;
    });
    return () => cancelAnimationFrame(id);
  }, []);

  const today = new Date();
  const todayKey = dayKey(today);
  // 本周一
  const monday = new Date(today.getFullYear(), today.getMonth(), today.getDate() - ((today.getDay() + 6) % 7));
  const start = new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() - (weeks - 1) * 7);

  const columns: { key: string; seconds: number; future: boolean }[][] = [];
  const months: string[] = [];
  let studiedDays = 0;
  let total = 0;
  for (let w = 0; w < weeks; w++) {
    const col = [];
    for (let d = 0; d < 7; d++) {
      const date = new Date(start.getFullYear(), start.getMonth(), start.getDate() + w * 7 + d);
      const key = dayKey(date);
      const seconds = days[key] ?? 0;
      const future = key > todayKey;
      if (!future && seconds >= 60) studiedDays++;
      if (!future) total += seconds;
      col.push({ key, seconds, future });
    }
    columns.push(col);
    // 月份标在这个月第一次出现的那一列上
    const m = new Date(`${col[0].key}T00:00:00`).getMonth();
    const prev = w > 0 ? new Date(`${columns[w - 1][0].key}T00:00:00`).getMonth() : -1;
    months.push(m !== prev && w > 0 ? `${m + 1}月` : "");
  }

  return (
    <div className="heatmap">
      <div className="heatmap-scroll" ref={scroller}>
        <div className="heatmap-grid" style={{ gridTemplateColumns: `auto repeat(${weeks}, minmax(var(--cell), 1fr))` }}>
          <span />
          {months.map((m, i) => (
            <span key={i} className="heatmap-month">
              {m}
            </span>
          ))}
          {ROW_LABELS.map((label, row) => (
            <Row key={row} label={label} row={row} columns={columns} todayKey={todayKey} />
          ))}
        </div>
      </div>
      <div className="heatmap-foot">
        <span>
          最近 {weeks} 周学了 <b>{studiedDays}</b> 天，共 <b>{formatDuration(total)}</b>
        </span>
        <span className="heatmap-legend">
          少
          {[0, 1, 2, 3, 4].map((l) => (
            <i key={l} className={`lv${l}`} />
          ))}
          多
        </span>
      </div>
    </div>
  );
}

function Row({
  label,
  row,
  columns,
  todayKey,
}: {
  label: string;
  row: number;
  columns: { key: string; seconds: number; future: boolean }[][];
  todayKey: string;
}) {
  return (
    <>
      <span className="heatmap-day">{label}</span>
      {columns.map((col) => {
        const c = col[row];
        if (c.future) return <i key={c.key} className="future" />;
        return (
          <i
            key={c.key}
            className={`lv${level(c.seconds)}${c.key === todayKey ? " today" : ""}`}
            title={`${c.key}：${c.seconds >= 60 ? formatDuration(c.seconds) : "没学"}`}
          />
        );
      })}
    </>
  );
}
