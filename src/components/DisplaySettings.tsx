"use client";

import { useEffect, useRef, useState } from "react";

import {
  applyPrefs,
  DEFAULT_PREFS,
  FONT_SIZES,
  loadPrefs,
  savePrefs,
  type Prefs,
} from "@/lib/prefs";

const SIZE_LABEL: Record<number, string> = {
  14: "小",
  16: "标准",
  18: "大",
  20: "特大",
};

/** 侧栏顶部的「Aa」按钮：点开调正文字号（浅色 / 深色切换在 ThemeToggle）。 */
export default function DisplaySettings() {
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS);
  const [open, setOpen] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  // 点外面或按 Esc 收起
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (!boxRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // 读保存的设置（<head> 里的脚本已经套上了，这里只是让按钮显示对）
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPrefs(loadPrefs());
  }, []);

  const update = (patch: Partial<Prefs>) => {
    // 主题由 ThemeToggle 改，这里重新读一次，避免把它刚改的主题盖回去
    const next = { ...loadPrefs(), ...patch };
    setPrefs(next);
    applyPrefs(next);
    savePrefs(next);
  };

  const i = FONT_SIZES.indexOf(prefs.fontSize as (typeof FONT_SIZES)[number]);

  return (
    <div className="display-settings" ref={boxRef}>
      <button
        type="button"
        className={`icon-btn font-btn ${open ? "active" : ""}`}
        onClick={() => setOpen((v) => !v)}
        aria-label="正文字号"
        aria-expanded={open}
        title="正文字号"
      >
        Aa
      </button>
      {open && (
        <div className="font-step" aria-label="正文字号">
          <button
            type="button"
            disabled={i <= 0}
            onClick={() => update({ fontSize: FONT_SIZES[i - 1] })}
            aria-label="字号调小"
            title="字号调小"
          >
            A−
          </button>
          <span title="正文字号">{SIZE_LABEL[prefs.fontSize]}</span>
          <button
            type="button"
            disabled={i >= FONT_SIZES.length - 1}
            onClick={() => update({ fontSize: FONT_SIZES[i + 1] })}
            aria-label="字号调大"
            title="字号调大"
          >
            A+
          </button>
        </div>
      )}
    </div>
  );
}
