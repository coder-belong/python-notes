/**
 * 页面语言：中文是原文，英文 / 日文由 AI 翻译（见 translate.ts）。选的语言存在浏览器里。
 * 用 useSyncExternalStore 订阅：菜单里一改，正文、侧栏、问 AI 都跟着变。
 */

import { useSyncExternalStore } from "react";

export type Lang = "zh" | "en" | "ja";
export const LANGS: { id: Lang; label: string; short: string }[] = [
  { id: "zh", label: "中文", short: "中" },
  { id: "en", label: "English", short: "EN" },
  { id: "ja", label: "日本語", short: "日" },
];

const KEY = "python-notes:lang";
const EVENT = "python-notes:lang";

export function loadLang(): Lang {
  try {
    const v = localStorage.getItem(KEY);
    return v === "en" || v === "ja" ? v : "zh";
  } catch {
    return "zh";
  }
}

export function setLang(lang: Lang): void {
  try {
    localStorage.setItem(KEY, lang);
  } catch {
    // 存不了就只对这次有效
  }
  current = lang;
  window.dispatchEvent(new Event(EVENT));
}

let current: Lang | null = null;

function subscribe(cb: () => void): () => void {
  window.addEventListener(EVENT, cb);
  return () => window.removeEventListener(EVENT, cb);
}

export function useLang(): Lang {
  return useSyncExternalStore(
    subscribe,
    () => (current ??= loadLang()),
    () => "zh", // 服务端渲染（静态导出）时一律中文
  );
}
