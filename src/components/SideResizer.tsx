"use client";

import { useEffect } from "react";

const KEY = "python-notes:side-w";
const MIN = 220;
const MAX = 560;
const DEFAULT = 360;

const clamp = (w: number) => Math.min(MAX, Math.max(MIN, Math.round(w)));

/** 改侧栏宽度：写到 CSS 变量 --side-w 上，侧栏和正文的左边距都跟着变。 */
function apply(w: number) {
  document.documentElement.style.setProperty("--side-w", `${w}px`);
}

/** 侧栏右边缘的拖拽条：拖动改宽度，双击恢复默认；宽度记在浏览器里。 */
export default function SideResizer() {
  // 打开页面时用上次的宽度
  useEffect(() => {
    try {
      const saved = Number(localStorage.getItem(KEY));
      if (saved) apply(clamp(saved));
    } catch {
      // 读不到就用默认宽度
    }
  }, []);

  const save = (w: number) => {
    try {
      localStorage.setItem(KEY, String(w));
    } catch {
      // 存不了就算了
    }
  };

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    e.preventDefault();
    const handle = e.currentTarget;
    handle.setPointerCapture(e.pointerId);
    document.body.classList.add("resizing");
    let width = clamp(document.querySelector("aside")?.getBoundingClientRect().width ?? DEFAULT);
    const onMove = (ev: PointerEvent) => {
      width = clamp(ev.clientX);
      apply(width);
    };
    const onUp = () => {
      handle.removeEventListener("pointermove", onMove);
      handle.removeEventListener("pointerup", onUp);
      handle.removeEventListener("pointercancel", onUp);
      document.body.classList.remove("resizing");
      save(width);
    };
    handle.addEventListener("pointermove", onMove);
    handle.addEventListener("pointerup", onUp);
    handle.addEventListener("pointercancel", onUp);
  };

  const onDoubleClick = () => {
    apply(DEFAULT);
    save(DEFAULT);
  };

  return (
    <div
      className="side-resizer"
      role="separator"
      aria-orientation="vertical"
      aria-label="拖动调整目录宽度"
      title="拖动调整宽度，双击恢复默认"
      onPointerDown={onPointerDown}
      onDoubleClick={onDoubleClick}
    />
  );
}
