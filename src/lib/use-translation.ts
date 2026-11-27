/**
 * 把页面上的笔记换成 AI 译文：
 * - 正文：找出 .sec-html 里一个个最小的文字块（段落、列表项、小标题、表格格子），
 *   把它们的 innerHTML 拿去翻译，翻好一批就替换一批；代码块、流程图不动。
 *   切回中文或换节时，把原来的 HTML 放回去。
 * - 侧栏：各阶段名、各节标题一起翻一次。
 */

import { useEffect, useState } from "react";

import type { Lang } from "./lang";
import type { Section } from "./notes";
import { translateItems } from "./translate";

const BLOCK = "h3,h4,h5,p,li,td,th,dt,dd,figcaption,summary";
const SKIP = "pre,code,.mermaid-box,.stream-demo,svg";
const HAS_CJK = /[㐀-鿿]/;

export type TrState = {
  status: "idle" | "loading" | "done" | "error";
  done: number; // 翻好了几段
  total: number;
  error: { status: number; msg: string } | null;
  title: string | null; // 译好的本节标题
  toc: Record<string, string>; // 小标题 id → 译文（右侧目录用）
};

const IDLE: TrState = { status: "idle", done: 0, total: 0, error: null, title: null, toc: {} };

/** 最小的文字块：本身是段落 / 列表项等，里面不再套别的块，且带中文。 */
function collectBlocks(root: Element): HTMLElement[] {
  const all = Array.from(root.querySelectorAll<HTMLElement>(BLOCK)).filter(
    (el) => !el.closest(SKIP) && HAS_CJK.test(el.textContent ?? ""),
  );
  return all.filter((el) => !all.some((o) => o !== el && el.contains(o)));
}

/** 译文是模型生成的 HTML：去掉脚本、事件属性、javascript: 链接再放进页面。 */
function sanitize(html: string): string {
  const tpl = document.createElement("template");
  tpl.innerHTML = html;
  tpl.content.querySelectorAll("script,style,iframe,object,embed,link,meta").forEach((n) => n.remove());
  tpl.content.querySelectorAll("*").forEach((el) => {
    for (const a of Array.from(el.attributes)) {
      if (a.name.startsWith("on") || /^\s*javascript:/i.test(a.value)) el.removeAttribute(a.name);
    }
  });
  return tpl.innerHTML;
}

export function useSectionTranslation(section: Section | null, lang: Lang, token: string | undefined): TrState {
  const [state, setState] = useState<TrState>(IDLE);

  useEffect(() => {
    if (!section || lang === "zh") {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setState(IDLE);
      return;
    }
    const root = document.querySelector(".sec-html");
    if (!root) return;
    const blocks = collectBlocks(root);
    const originals = blocks.map((b) => b.innerHTML);
    const items = [section.title, ...originals];
    let cancelled = false;
    let done = 0;
    setState({ ...IDLE, status: "loading", total: items.length });

    void translateItems(
      items,
      lang,
      token,
      (start, out) => {
        let title: string | null = null;
        const toc: Record<string, string> = {};
        out.forEach((html, k) => {
          const i = start + k;
          if (i === 0) title = html;
          else {
            const el = blocks[i - 1];
            el.innerHTML = sanitize(html);
            if (el.tagName === "H3" && el.id) toc[el.id] = el.textContent ?? "";
          }
        });
        done += out.length;
        setState((s) => ({ ...s, done, title: title ?? s.title, toc: { ...s.toc, ...toc } }));
      },
      () => cancelled,
    ).then((error) => {
      if (cancelled) return;
      setState((s) => ({ ...s, status: error ? "error" : "done", error }));
    });

    return () => {
      cancelled = true;
      blocks.forEach((b, i) => {
        b.innerHTML = originals[i]; // 切回中文 / 换节：还原
      });
    };
  }, [section, lang, token]);

  return state;
}

/** 侧栏、面包屑、上一节 / 下一节里的阶段名和节标题：一起翻，返回「原文 → 译文」。 */
export function useNavTranslation(sections: Section[], lang: Lang, token: string | undefined): Map<string, string> {
  const [map, setMap] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMap(new Map());
    if (lang === "zh") return;
    const items = Array.from(new Set(sections.flatMap((s) => [s.name, ...(s.part ? [s.part] : [])])));
    let cancelled = false;
    void translateItems(
      items,
      lang,
      token,
      (start, out) =>
        setMap((m) => {
          const n = new Map(m);
          out.forEach((t, k) => n.set(items[start + k], t));
          return n;
        }),
      () => cancelled,
    );
    return () => {
      cancelled = true;
    };
  }, [sections, lang, token]);

  return map;
}
