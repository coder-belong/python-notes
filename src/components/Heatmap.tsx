"use client";

import { useEffect, useRef, useState } from "react";

import { dayKey, formatDuration, STUDIED_DAY_SECONDS } from "@/lib/study-store";

/** 每天学了多久 → 颜色深浅 0~4 档：不满 10 分钟不亮，10～20 分、20～40 分、40～60 分、1 小时以上。 */
function level(seconds: number): number {
  if (seconds < STUDIED_DAY_SECONDS) return 0;
  if (seconds < 20 * 60) return 1;
  if (seconds < 40 * 60) return 2;
  if (seconds < 60 * 60) return 3;
  return 4;
}

/** 悬停提示的文字：「11月18日 周二 · 学了 25 分」。 */
function tipText(key: string, seconds: number): string {
  const d = new Date(`${key}T00:00:00`);
  const date = `${d.getMonth() + 1}月${d.getDate()}日 周${"日一二三四五六"[d.getDay()]}`;
  if (seconds <= 0) return `${date} · 没学`;
  const spent = `学了 ${formatDuration(seconds)}`;
  return seconds < STUDIED_DAY_SECONDS ? `${date} · ${spent}（不满 10 分钟，不点亮）` : `${date} · ${spent}`;
}

/** align：靠近屏幕左右边时提示框往里靠，不超出屏幕。 */
type Tip = { text: string; x: number; y: number; align: "center" | "left" | "right" };

const ROW_LABELS = ["一", "", "三", "", "五", "", "日"];

type Props = {
  days: Record<string, number>;
  /** 显示最近多少周（最后一列是本周）。 */
  weeks?: number;
};

/** 学习热力图：一格一天，一列一周（周一在上），颜色越深学得越久。 */
export default function Heatmap({ days, weeks = 53 }: Props) {
  const scroller = useRef<HTMLDivElement>(null);
  const [tip, setTip] = useState<Tip | null>(null);

  // 鼠标移到某一格上：在格子正上方显示提示（用 fixed 定位，不会被横向滚动的容器裁掉）
  const showTip = (e: React.MouseEvent) => {
    const cell = (e.target as HTMLElement).closest<HTMLElement>("i[data-day]");
    if (!cell) return setTip(null);
    const r = cell.getBoundingClientRect();
    const x = r.left + r.width / 2;
    const align = x < 160 ? "left" : x > window.innerWidth - 160 ? "right" : "center";
    setTip({ text: tipText(cell.dataset.day!, Number(cell.dataset.sec)), x, y: r.top, align });
  };

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
      if (!future && seconds >= STUDIED_DAY_SECONDS) studiedDays++;
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
      <div className="heatmap-scroll" ref={scroller} onScroll={() => setTip(null)}>
        <div
          className="heatmap-grid"
          onMouseOver={showTip}
          onClick={showTip}
          onMouseLeave={() => setTip(null)} style={{ gridTemplateColumns: `auto repeat(${weeks}, minmax(var(--cell), 1fr))` }}>
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
      {tip && (
        <div className={`heatmap-tip ${tip.align}`} style={{ left: tip.x, top: tip.y }} role="tooltip">
          {tip.text}
        </div>
      )}
      <div className="heatmap-foot">
        <span>
          最近 {weeks} 周有 <b>{studiedDays}</b> 天学满 10 分钟，共 <b>{formatDuration(total)}</b>
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
            data-day={c.key}
            data-sec={c.seconds}
          />
        );
      })}
    </>
  );
}
