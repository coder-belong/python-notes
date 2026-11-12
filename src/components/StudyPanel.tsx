"use client";

import { useEffect, useState } from "react";

import Heatmap from "./Heatmap";

import type { Section } from "@/lib/notes";
import { dayKey, formatClock, formatDuration, lastDays, longestStreak, streak } from "@/lib/study-store";
import type { useStudy } from "@/lib/use-study";

type Study = ReturnType<typeof useStudy>;

const STATUS_TEXT = {
  studying: "学习中",
  idle: "已暂停 · 90 秒没操作",
  hidden: "已暂停 · 页面不在前台",
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

/** 默认只列用时最多的几节，其余的点「显示全部」。 */
const TOP_SECTIONS = 6;

/** 点开入口后的弹窗：顶部四个数字，中间热力图，下面左边最近 7 天、右边每节用时。 */
export default function StudyPanel({ study, sections, onClose }: Props) {
  const { data, sessionSeconds, status } = study;
  const [showAll, setShowAll] = useState(false);
  const todayKey = dayKey();
  const today = data.days[todayKey] ?? 0;
  const totalSeconds = Object.values(data.days).reduce((a, b) => a + b, 0);
  const studiedDays = Object.values(data.days).filter((s) => s >= 60).length;
  const week = lastDays(7);
  const weekSeconds = week.reduce((a, d) => a + (data.days[d] ?? 0), 0);
  const weekMax = Math.max(60, ...week.map((d) => data.days[d] ?? 0));
  const doneCount = sections.filter((s) => data.done[s.id]).length;
  const bySection = sections
    .map((s) => ({ ...s, seconds: data.sections[s.id] ?? 0 }))
    .filter((s) => s.seconds > 0)
    .sort((a, b) => b.seconds - a.seconds);
  const sectionMax = Math.max(1, ...bySection.map((s) => s.seconds));
  const shown = showAll ? bySection : bySection.slice(0, TOP_SECTIONS);
  const pomodoros = data.pomodoros[todayKey] ?? 0;

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
      <div className="modal stats-modal" role="dialog" aria-label="学习统计" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>学习统计</h3>
          <span className={`study-now ${status}`}>
            <span className="pulse" />
            {STATUS_TEXT[status]}
            <span className="clock">本次 {formatClock(sessionSeconds)}</span>
          </span>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>

        <div className="stat-cards">
          <div className="stat-card accent">
            <span className="stat-label">今天</span>
            <b>{formatDuration(today)}</b>
            <span className="stat-sub">{pomodoros > 0 ? `完成 ${pomodoros} 个番茄钟` : "还没有番茄钟"}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">累计</span>
            <b>{formatDuration(totalSeconds)}</b>
            <span className="stat-sub">学了 {studiedDays} 天</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">连续学习</span>
            <b>{streak(data.days)} 天</b>
            <span className="stat-sub">最长 {longestStreak(data.days)} 天</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">已学完</span>
            <b>
              {doneCount}
              <small> / {sections.length} 节</small>
            </b>
            <span className="stat-progress">
              <i style={{ width: `${(doneCount / sections.length) * 100}%` }} />
            </span>
          </div>
        </div>

        <section className="stats-box">
          <h4>学习热力图</h4>
          <Heatmap days={data.days} weeks={53} />
        </section>

        <div className="stats-cols">
          <section className="stats-box">
            <h4>
              最近 7 天<span className="stats-box-note">共 {formatDuration(weekSeconds)}</span>
            </h4>
            <div className="week" aria-label="最近 7 天学习时长">
              {week.map((d) => {
                const sec = data.days[d] ?? 0;
                const wd = WEEKDAY[new Date(`${d}T00:00:00`).getDay()];
                const isToday = d === todayKey;
                return (
                  <div key={d} className={`week-col ${isToday ? "today" : ""}`} title={`${d}：${formatDuration(sec)}`}>
                    <em>{sec >= 60 ? `${Math.round(sec / 60)}分` : ""}</em>
                    <div className="week-bar">
                      {sec > 0 && <i style={{ height: `${Math.max(4, Math.round((sec / weekMax) * 100))}%` }} />}
                    </div>
                    <span>{isToday ? "今天" : `周${wd}`}</span>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="stats-box">
            <h4>
              每节用时<span className="stats-box-note">{bySection.length} 节有记录</span>
            </h4>
            {bySection.length === 0 ? (
              <p className="hint">还没有记录：在页面上阅读、滚动时，会记到当前读到的那一节上。</p>
            ) : (
              <ul className="sec-list">
                {shown.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`} onClick={onClose} title={s.title}>
                      {s.num && <span className="sec-num">{s.num}</span>}
                      <span className="sec-list-name">{s.name}</span>
                    </a>
                    <span className="sec-list-time">{formatDuration(s.seconds)}</span>
                    <span className="sec-list-bar">
                      <i style={{ width: `${(s.seconds / sectionMax) * 100}%` }} />
                    </span>
                  </li>
                ))}
              </ul>
            )}
            {bySection.length > TOP_SECTIONS && (
              <button type="button" className="link-btn" onClick={() => setShowAll((v) => !v)}>
                {showAll ? "收起" : `显示全部 ${bySection.length} 节`}
              </button>
            )}
          </section>
        </div>

        <div className="stats-foot">
          <span>
            页面在前台、并且 90 秒内有滚动 / 鼠标 / 键盘操作时才计时。
            {study.account ? `记录同步在账号「${study.account.username}」上。` : "没登录时记录只保存在这个浏览器里。"}
          </span>
          {!study.account && (
            <button type="button" className="link-btn" onClick={onReset}>
              清空记录
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
