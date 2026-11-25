"use client";

import { useEffect, useMemo } from "react";

import {
  formatDayWithWeek,
  progressEvents,
  type ProgressEvent,
} from "@/lib/progress";
import { dayKey, type StudyData } from "@/lib/study-store";

import type { Group } from "./NotesApp";

import "./ProgressDrawer.css";
import { blurActive } from "@/lib/blur";

type Props = {
  groups: Group[];
  data: StudyData;
  onClose: () => void;
};

const KIND_LABEL: Record<ProgressEvent["kind"], string> = {
  "stage-done": "🎉 学完阶段",
  done: "学完",
  start: "开始学",
  "stage-start": "开始阶段",
};

/** 学习过程抽屉（首页「学习热力图」旁边点开）：按天列出开始学、学完的节和阶段，新的在上。 */
export default function ProgressDrawer({ groups, data, onClose }: Props) {
  const today = dayKey();
  const events = useMemo(() => progressEvents(groups, data), [groups, data]);
  const all = groups.flatMap((g) => g.items);
  const doneCount = all.filter((s) => data.done[s.id]).length;
  const stagesDone = events.filter((e) => e.kind === "stage-done").length;

  // Esc 关闭
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      blurActive(); // 不然打开弹窗的那个按钮会留下一圈焦点框
      onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  // 按天分组
  const byDay: { day: string; items: ProgressEvent[] }[] = [];
  for (const e of events) {
    const last = byDay.at(-1);
    if (last && last.day === e.day) last.items.push(e);
    else byDay.push({ day: e.day, items: [e] });
  }

  return (
    <div
      className="drawer-backdrop"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <section className="progress-drawer" aria-label="学习过程">
        <div className="drawer-head">
          <h3>学习过程</h3>
          <button
            type="button"
            className="modal-close"
            onClick={onClose}
            aria-label="关闭（Esc）"
            title="关闭（Esc）"
          >
            ×
          </button>
        </div>
        <div
          className="drawer-body"
          onClick={(e) => (e.target as HTMLElement).closest("a") && onClose()}
        >
          <p className="hint">
            已学完 {doneCount} / {all.length} 节
            {stagesDone > 0 && `，学完 ${stagesDone} 个阶段`}
            。第一次学某一节时记下开始日期，勾「学完了」时记下学完日期。
          </p>

          {events.length === 0 ? (
            <p className="sproc-empty">
              还没有记录。开始学新的一节、勾「学完了」，这里会按天记下来。
            </p>
          ) : (
            <div className="sproc">
              {byDay.map((d) => (
                <section key={d.day} className="sproc-day">
                  <h3>
                    {d.day === today
                      ? `今天 · ${formatDayWithWeek(d.day)}`
                      : formatDayWithWeek(d.day)}
                  </h3>
                  <ul>
                    {d.items.map((e, i) => (
                      <li key={i} className={`sproc-item ${e.kind}`}>
                        <span className="sproc-tag">{KIND_LABEL[e.kind]}</span>
                        <a href={e.href}>{e.text}</a>
                      </li>
                    ))}
                  </ul>
                </section>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
