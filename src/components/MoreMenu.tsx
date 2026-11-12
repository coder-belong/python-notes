"use client";

import { useEffect, useRef, useState } from "react";

import { applyPrefs, DEFAULT_PREFS, FONT_SIZES, loadPrefs, savePrefs, type Prefs } from "@/lib/prefs";

const SIZE_LABEL: Record<number, string> = {
  14: "小",
  16: "标准",
  18: "大",
  20: "特大",
};

type Props = {
  /** 更新日志里有没看过的新内容：按钮和菜单项上显示小红点。 */
  hasNew: boolean;
  onOpenChangelog: () => void;
  collapsed: boolean;
  onToggleSidebar: () => void;
  /** 菜单往哪边弹：侧栏展开时往下，收起成窄条时往右。 */
  placement: "down" | "right";
};

/**
 * 侧栏顶部的「⋯」：不常用的设置和入口都收在这里（正文字号、更新日志、收起侧栏），
 * 以后再加设置项也往这里放，侧栏顶部不再加按钮。浅色 / 深色切换常用，单独放在外面。
 */
export default function MoreMenu({ hasNew, onOpenChangelog, collapsed, onToggleSidebar, placement }: Props) {
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS);
  const [open, setOpen] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  // 读保存的字号（<head> 里的脚本已经套上了，这里只是让按钮显示对）
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPrefs(loadPrefs());
  }, []);

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

  const update = (patch: Partial<Prefs>) => {
    // 主题由 ThemeToggle 改，这里重新读一次，避免把它刚改的主题盖回去
    const next = { ...loadPrefs(), ...patch };
    setPrefs(next);
    applyPrefs(next);
    savePrefs(next);
  };

  const i = FONT_SIZES.indexOf(prefs.fontSize as (typeof FONT_SIZES)[number]);

  return (
    <div className="more-menu" ref={boxRef}>
      <button
        type="button"
        className={`icon-btn ${open ? "active" : ""}`}
        onClick={() => setOpen((v) => !v)}
        aria-label="更多：字号、更新日志"
        aria-expanded={open}
        title="更多"
      >
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <circle cx="5" cy="12" r="1.8" fill="currentColor" />
          <circle cx="12" cy="12" r="1.8" fill="currentColor" />
          <circle cx="19" cy="12" r="1.8" fill="currentColor" />
        </svg>
        {hasNew && <span className="new-dot" />}
      </button>

      {open && (
        <div className={`menu-pop ${placement}`} role="menu">
          <div className="menu-row">
            <span>正文字号</span>
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
              <span>{SIZE_LABEL[prefs.fontSize]}</span>
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
          </div>
          <div className="menu-sep" />
          <button
            type="button"
            role="menuitem"
            className="menu-item"
            onClick={() => {
              setOpen(false);
              onOpenChangelog();
            }}
          >
            <span>更新日志</span>
            {hasNew && <span className="menu-badge">新</span>}
          </button>
          <button
            type="button"
            role="menuitem"
            className="menu-item hide-narrow"
            onClick={() => {
              setOpen(false);
              onToggleSidebar();
            }}
          >
            <span>{collapsed ? "展开侧栏" : "收起侧栏"}</span>
            <kbd>\</kbd>
          </button>
        </div>
      )}
    </div>
  );
}
