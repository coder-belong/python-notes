"use client";

import { useEffect } from "react";

import Heatmap from "./Heatmap";

import type { Section } from "@/lib/notes";
import { dayKey, formatClock, formatDuration, lastDays, streak } from "@/lib/study-store";
import type { useStudy } from "@/lib/use-study";

type Study = ReturnType<typeof useStudy>;

const STATUS_TEXT = {
  studying: "学习中",
  idle: "已暂停（90 秒没操作）",
  hidden: "已暂停（页面不在前台）",
} as const;

const WEEKDAY = ["日", "一", "二", "三", "四", "五", "六"];

/** 侧边栏里的入口：只显示状态和今天学了多久，点开看详细统计。 */
export function StudyEntry({ study, onOpen }: { study: Study; onOpen: () => void }) {
  const today = study.data.days[dayKey()] ?? 0;
  return (
    <button type="button" className={`study-entry ${study.status}`} onClick={onOpen} title="查看学习统计">
      <span className="pulse" />
      <span>今天 {formatDuration(today)}</span>
      <span className="study-entry-more">学习统计 ›</span>
    </button>
  );
}

type Props = {
  study: Study;
  sections: Section[];
  onClose: () => void;
};

/** 点开入口后的弹窗：本次计时、今天 / 累计 / 连续天数、最近 7 天、每节用时。 */
export default function StudyPanel({ study, sections, onClose }: Props) {
  const { data, sessionSeconds, status } = study;
  const today = data.days[dayKey()] ?? 0;
  const totalSeconds = Object.values(data.days).reduce((a, b) => a + b, 0);
  const week = lastDays(7);
  const weekMax = Math.max(60, ...week.map((d) => data.days[d] ?? 0));
  const doneCount = sections.filter((s) => data.done[s.id]).length;
  const bySection = sections
    .map((s) => ({ ...s, seconds: data.sections[s.id] ?? 0 }))
    .filter((s) => s.seconds > 0)
    .sort((a, b) => b.seconds - a.seconds);
  const sectionMax = Math.max(1, ...bySection.map((s) => s.seconds));

  // Esc 关闭
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const onReset = () => {
    if (window.confirm("清空所有学习时长和「学完了」记录？清空后不能恢复。")) study.reset();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" role="dialog" aria-label="学习统计" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>学习统计</h3>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>

        <div className={`study-now ${status}`}>
          <span className="pulse" />
          <span>{STATUS_TEXT[status]}</span>
          <span className="clock">本次 {formatClock(sessionSeconds)}</span>
        </div>

        <div className="study-grid">
          <div>
            <b>{formatDuration(today)}</b>
            <span>今天</span>
          </div>
          <div>
            <b>{formatDuration(totalSeconds)}</b>
            <span>累计</span>
          </div>
          <div>
            <b>{streak(data.days)} 天</b>
            <span>连续学习</span>
          </div>
          <div>
            <b>
              {doneCount}/{sections.length}
            </b>
            <span>已学完</span>
          </div>
        </div>

        <h4>学习热力图</h4>
        <Heatmap days={data.days} weeks={26} />
        <p className="hint">今天完成了 {data.pomodoros[dayKey()] ?? 0} 个番茄钟（专注模式里专注满 25 分钟算一个）</p>

        <h4>最近 7 天</h4>
        <div className="week" aria-label="最近 7 天学习时长">
          {week.map((d) => {
            const sec = data.days[d] ?? 0;
            const wd = WEEKDAY[new Date(`${d}T00:00:00`).getDay()];
            return (
              <div key={d} className="week-col" title={`${d}：${formatDuration(sec)}`}>
                <em>{sec >= 60 ? Math.round(sec / 60) : ""}</em>
                <div className="week-bar">
                  <i style={{ height: `${Math.round((sec / weekMax) * 100)}%` }} />
                </div>
                <span>{d === dayKey() ? "今" : wd}</span>
              </div>
            );
          })}
        </div>
        <p className="hint">柱子上的数字是分钟</p>

        <h4>每节用时</h4>
        {bySection.length === 0 ? (
          <p className="hint">还没有记录：在页面上阅读、滚动时，会记到当前读到的那一节上</p>
        ) : (
          <ul className="sec-list">
            {bySection.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`} onClick={onClose}>
                  {s.title}
                </a>
                <span className="sec-list-bar">
                  <i style={{ width: `${(s.seconds / sectionMax) * 100}%` }} />
                </span>
                <span className="sec-list-time">{formatDuration(s.seconds)}</span>
              </li>
            ))}
          </ul>
        )}

        <p className="hint">
          页面在前台、并且 90 秒内有滚动 / 鼠标 / 键盘操作时才计时。
          {study.account ? `记录同步在账号「${study.account.username}」上。` : "没登录时记录只保存在这个浏览器里。"}
        </p>
        {!study.account && (
          <button type="button" className="reset" onClick={onReset}>
            清空记录
          </button>
        )}
      </div>
    </div>
  );
}
