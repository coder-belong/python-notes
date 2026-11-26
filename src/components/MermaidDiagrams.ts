/**
 * 笔记里的流程图：notes.ts 把 ```mermaid 代码块输出成 <pre class="mermaid-src">（里面是图的文字描述），
 * 这里在浏览器里加载 mermaid，把它们画成 SVG。mermaid 很大，只在页面上真的有流程图时才加载。
 */

import "./MermaidDiagrams.css";

let counter = 0;

function isDark(): boolean {
  const t = document.documentElement.dataset.theme;
  return t === "dark" || (t !== "light" && window.matchMedia("(prefers-color-scheme: dark)").matches);
}

/** 把正文里所有还没画的流程图画出来。返回清理函数（换节时组件会重新调用）。 */
export function renderMermaid(): () => void {
  let cancelled = false;
  const blocks = Array.from(document.querySelectorAll<HTMLPreElement>(".sec-html pre.mermaid-src"));
  if (!blocks.length) return () => {};

  void import("mermaid")
    .then(async ({ default: mermaid }) => {
      mermaid.initialize({
        startOnLoad: false,
        theme: isDark() ? "dark" : "neutral",
        fontFamily: "inherit",
        themeVariables: { fontSize: "13px" }, // 比正文小一点，图不会撑得太大
        // useMaxWidth: false：按图本来的大小画，不拉伸撑满整行（小图拉大了会很占地方）
        flowchart: { curve: "basis", htmlLabels: true, useMaxWidth: false },
        sequence: { useMaxWidth: false },
      });
      for (const pre of blocks) {
        if (cancelled || !pre.isConnected) return;
        try {
          const { svg } = await mermaid.render(`mermaid-${++counter}`, pre.textContent ?? "");
          const box = document.createElement("div");
          box.className = "mermaid-box";
          box.innerHTML = svg;
          pre.replaceWith(box);
        } catch {
          pre.classList.add("mermaid-error"); // 画不出来就保留文字描述，至少能看
        }
      }
    })
    .catch(() => {
      // 单文件 HTML 版本里加载不到 mermaid：保留文字描述
    });
  return () => {
    cancelled = true;
  };
}
