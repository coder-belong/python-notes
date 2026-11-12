/** 显示设置：主题和正文字号，存在浏览器里。 */

export type Theme = "system" | "light" | "dark";
export type Prefs = { theme: Theme; fontSize: number };

export const PREFS_KEY = "python-notes:prefs";
export const FONT_SIZES = [14, 16, 18, 20] as const;
export const DEFAULT_PREFS: Prefs = { theme: "system", fontSize: 16 };

export function loadPrefs(): Prefs {
  try {
    const p = JSON.parse(localStorage.getItem(PREFS_KEY) ?? "{}") as Partial<Prefs>;
    return {
      theme: p.theme === "light" || p.theme === "dark" ? p.theme : "system",
      fontSize: FONT_SIZES.includes(p.fontSize as never) ? (p.fontSize as number) : DEFAULT_PREFS.fontSize,
    };
  } catch {
    return DEFAULT_PREFS;
  }
}

export function savePrefs(p: Prefs): void {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(p));
  } catch {
    // 存不了就只对这次有效
  }
}

/** 主题写到 <html data-theme>，字号写到 CSS 变量 --fs。 */
export function applyPrefs(p: Prefs): void {
  const root = document.documentElement;
  if (p.theme === "system") delete root.dataset.theme;
  else root.dataset.theme = p.theme;
  root.style.setProperty("--fs", `${p.fontSize}px`);
}

/**
 * 放在 <head> 里、页面画出来之前就执行的脚本：先套上保存的主题和字号，
 * 否则选了深色的话，每次打开会先闪一下浅色。逻辑和 applyPrefs 一样。
 */
/** 侧栏是否收起成窄条（只在宽屏有效，窄屏侧栏本来就是抽屉）。 */
export const SIDE_COLLAPSED_KEY = "python-notes:side-collapsed";

export const PREFS_BOOT_SCRIPT = `try{if(localStorage.getItem(${JSON.stringify("python-notes:side-collapsed")})==="1")document.documentElement.classList.add("side-collapsed")}catch(e){}try{var p=JSON.parse(localStorage.getItem(${JSON.stringify(PREFS_KEY)})||"{}"),r=document.documentElement;if(p.theme==="light"||p.theme==="dark")r.dataset.theme=p.theme;if(p.fontSize)r.style.setProperty("--fs",p.fontSize+"px")}catch(e){}`;
