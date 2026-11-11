"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { dayKey, emptyData, loadData, saveData, type StudyData } from "./study-store";

/** 多久没操作就暂停计时。 */
const IDLE_SECONDS = 90;
/** 多久写一次 localStorage。 */
const SAVE_EVERY = 10;

export type StudyStatus = "studying" | "idle" | "hidden";

/**
 * 在线学习时长：页面在前台、窗口有焦点、并且最近 90 秒内有过滚动 / 鼠标 / 键盘操作时，每秒记 1 秒，
 * 同时记到「今天」和「当前读到的小节」上。切到别的标签页、离开电脑都会自动暂停。
 */
export function useStudy(currentSection: string | null) {
  const [data, setData] = useState<StudyData>(emptyData);
  const [loaded, setLoaded] = useState(false);
  const [sessionSeconds, setSessionSeconds] = useState(0);
  const [status, setStatus] = useState<StudyStatus>("studying");

  const dataRef = useRef<StudyData>(data);
  const sectionRef = useRef<string | null>(currentSection);
  const lastActiveRef = useRef<number>(0);
  const unsavedRef = useRef(0);

  useEffect(() => {
    sectionRef.current = currentSection;
  }, [currentSection]);

  // 首次进入：读出保存的记录（只能在浏览器里读 localStorage）
  useEffect(() => {
    const saved = loadData();
    dataRef.current = saved;
    lastActiveRef.current = Date.now();
    // 读 localStorage 只能放在 effect 里，读完再同步到 state
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setData(saved);
    setLoaded(true);
  }, []);

  const flush = useCallback(() => {
    saveData(dataRef.current);
    unsavedRef.current = 0;
  }, []);

  // 记录用户操作，判断是否在学
  useEffect(() => {
    const markActive = () => {
      lastActiveRef.current = Date.now();
    };
    const events = ["mousemove", "mousedown", "keydown", "scroll", "wheel", "touchstart"] as const;
    events.forEach((e) => window.addEventListener(e, markActive, { passive: true }));
    const onHide = () => {
      if (document.visibilityState === "hidden") flush();
      else markActive();
    };
    document.addEventListener("visibilitychange", onHide);
    window.addEventListener("pagehide", flush);
    return () => {
      events.forEach((e) => window.removeEventListener(e, markActive));
      document.removeEventListener("visibilitychange", onHide);
      window.removeEventListener("pagehide", flush);
    };
  }, [flush]);

  // 每秒判断一次：在学就加 1 秒
  useEffect(() => {
    if (!loaded) return;
    const timer = window.setInterval(() => {
      const visible = document.visibilityState === "visible" && document.hasFocus();
      const recent = Date.now() - lastActiveRef.current < IDLE_SECONDS * 1000;
      const next: StudyStatus = !visible ? "hidden" : recent ? "studying" : "idle";
      setStatus(next);
      if (next !== "studying") return;

      const today = dayKey();
      const prev = dataRef.current;
      const section = sectionRef.current;
      const updated: StudyData = {
        ...prev,
        days: { ...prev.days, [today]: (prev.days[today] ?? 0) + 1 },
        sections: section ? { ...prev.sections, [section]: (prev.sections[section] ?? 0) + 1 } : prev.sections,
      };
      dataRef.current = updated;
      setData(updated);
      setSessionSeconds((s) => s + 1);

      unsavedRef.current += 1;
      if (unsavedRef.current >= SAVE_EVERY) flush();
    }, 1000);
    return () => window.clearInterval(timer);
  }, [loaded, flush]);

  const toggleDone = useCallback(
    (id: string) => {
      const prev = dataRef.current;
      const updated = { ...prev, done: { ...prev.done, [id]: !prev.done[id] } };
      dataRef.current = updated;
      setData(updated);
      flush();
    },
    [flush],
  );

  /** 专注模式里完成一个番茄钟：记到今天。 */
  const addPomodoro = useCallback(() => {
    const prev = dataRef.current;
    const today = dayKey();
    const updated = { ...prev, pomodoros: { ...prev.pomodoros, [today]: (prev.pomodoros[today] ?? 0) + 1 } };
    dataRef.current = updated;
    setData(updated);
    flush();
  }, [flush]);

  const reset = useCallback(() => {
    const fresh = emptyData();
    dataRef.current = fresh;
    setData(fresh);
    setSessionSeconds(0);
    flush();
  }, [flush]);

  return { data, loaded, sessionSeconds, status, toggleDone, addPomodoro, reset };
}
