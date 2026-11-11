"use client";

import { useEffect, useState } from "react";

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

/** 侧栏里的正文字号调节（浅色 / 深色切换在 ThemeToggle）。 */
export default function DisplaySettings() {
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS);

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
    <div className="display-settings">
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
    </div>
  );
}
