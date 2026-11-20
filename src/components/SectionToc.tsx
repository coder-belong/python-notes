"use client";

import { useEffect, useState, type ReactNode } from "react";

import type { TocItem } from "@/lib/notes";

/** 正文区宽度够放「文字 + 右侧目录」时才显示目录（不含左右内边距）：文字至少留 640px 左右。 */
const WIDE_ENOUGH = 900;
/** 小标题滚到离窗口顶部这么近，就算「读到这里了」。 */
const ACTIVE_OFFSET = 120;

/**
 * 一节的布局：左边正文，右边「本节目录」。
 * 正文区不够宽（窄屏、侧栏拉得很宽）或小标题少于 2 个时，只有正文，不显示目录。
 */
export default function SectionLayout({ toc, children }: { toc: TocItem[]; children: ReactNode }) {
  const wide = useMainWide();
  const show = wide && toc.length >= 2;
  return (
    <div className={`sec-layout ${show ? "with-toc" : ""}`}>
      <div className="sec-main">{children}</div>
      {show && <SectionToc items={toc} />}
    </div>
  );
}

/** 监听 <main> 的宽度：侧栏收起、拖宽、进专注模式、窗口缩放都会变。 */
function useMainWide(): boolean {
  const [wide, setWide] = useState(false);
  useEffect(() => {
    const main = document.querySelector("main");
    if (!main) return;
    const update = () => {
      const style = getComputedStyle(main);
      const inner = main.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
      setWide(inner >= WIDE_ENOUGH);
    };
    const ro = new ResizeObserver(update); // observe 后会先回调一次，不用手动算第一次
    ro.observe(main);
    return () => ro.disconnect();
  }, []);
  return wide;
}

function SectionToc({ items }: { items: TocItem[] }) {
  const [active, setActive] = useState<string | null>(null);

  // 滚动时高亮「最后一个已经滚到顶部附近的小标题」
  useEffect(() => {
    const update = () => {
      let current: string | null = items[0].id; // 还没滚到第一个小标题时，也先亮第一个
      for (const item of items) {
        const el = document.getElementById(item.id);
        if (el && el.getBoundingClientRect().top <= ACTIVE_OFFSET) current = item.id;
      }
      // 滚到页面最底部时，最后几个小标题可能永远到不了顶部：直接算最后一个
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
        current = items[items.length - 1].id;
      }
      setActive(current);
    };
    const first = requestAnimationFrame(update); // 等这一帧渲染完再算，小标题才有位置
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      cancelAnimationFrame(first);
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [items]);

  // 点击只滚动，不改网址的 #：# 是用来切换「节」的
  const jump = (id: string) => {
    const el = document.getElementById(id);
    if (!el) return;
    const smooth = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    el.scrollIntoView({ behavior: smooth ? "smooth" : "instant", block: "start" });
  };

  return (
    <nav className="sec-toc" aria-label="本节目录">
      <div className="sec-toc-title">本节目录</div>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              className={active === item.id ? "active" : ""}
              aria-current={active === item.id ? "location" : undefined}
              onClick={() => jump(item.id)}
              title={item.text}
            >
              {item.text}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
