"use client";

import { useEffect, useState } from "react";
import { flushSync } from "react-dom";

import { applyPrefs, loadPrefs, savePrefs } from "@/lib/prefs";

/**
 * 浅色 / 深色切换：太阳和月亮之间有变形动画；
 * 换主题时新颜色从按钮的位置画圆扩散到整个页面（浏览器支持 View Transitions 时）。
 */
export default function ThemeToggle() {
  const [dark, setDark] = useState(false);

  // 现在实际是深色还是浅色：手动选过就按选的，没选过就跟系统；系统切换时也跟着变
  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const sync = () => {
      const { theme } = loadPrefs();
      setDark(theme === "dark" || (theme === "system" && mq.matches));
    };
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);

  const toggle = (e: React.MouseEvent<HTMLButtonElement>) => {
    const next = { ...loadPrefs(), theme: dark ? "light" : "dark" } as const;
    savePrefs(next);
    const swap = () => {
      applyPrefs(next);
      flushSync(() => setDark(!dark));
    };

    const reduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    if (!document.startViewTransition || reduced) {
      swap();
      return;
    }

    // 圆心是按钮中心，半径要能盖住离它最远的那个角
    const rect = e.currentTarget.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const radius = Math.hypot(
      Math.max(x, innerWidth - x),
      Math.max(y, innerHeight - y),
    );

    const transition = document.startViewTransition(swap);
    transition.ready.then(() => {
      document.documentElement.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${radius}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 550,
          easing: "cubic-bezier(0.4, 0, 0.2, 1)",
          pseudoElement: "::view-transition-new(root)",
        },
      );
    });
  };

  const label = dark ? "切换到浅色" : "切换到深色";
  return (
    <button
      type="button"
      className={`theme-toggle ${dark ? "is-dark" : ""}`}
      onClick={toggle}
      aria-label={label}
      title={label}
    >
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <mask id="theme-moon-cut">
          <rect width="24" height="24" fill="white" />
          <circle className="moon-cut" cx="17" cy="7" r="7" fill="black" />
        </mask>
        <circle
          className="sun-core"
          cx="12"
          cy="12"
          r="9"
          fill="currentColor"
          mask="url(#theme-moon-cut)"
        />
        <g
          className="sun-rays"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        >
          <line x1="12" y1="1.5" x2="12" y2="3.5" />
          <line x1="12" y1="20.5" x2="12" y2="22.5" />
          <line x1="1.5" y1="12" x2="3.5" y2="12" />
          <line x1="20.5" y1="12" x2="22.5" y2="12" />
          <line x1="4.6" y1="4.6" x2="6" y2="6" />
          <line x1="18" y1="18" x2="19.4" y2="19.4" />
          <line x1="4.6" y1="19.4" x2="6" y2="18" />
          <line x1="18" y1="6" x2="19.4" y2="4.6" />
        </g>
      </svg>
    </button>
  );
}
