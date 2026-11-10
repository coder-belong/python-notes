// 把 next build 导出的 out/index.html 打成一个独立的 HTML：CSS、JS 全部内联，双击就能打开，也可以单独拷走。
// 用法：npm run build（会自动跑这个脚本），产物在 dist/Python入门笔记.html
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const outDir = path.join(root, "out");
const distDir = path.join(root, "dist");
const target = path.join(distDir, "Python入门笔记.html");

const read = (src) => readFileSync(path.join(outDir, src.replace(/^\//, "")), "utf-8");

let html = readFileSync(path.join(outDir, "index.html"), "utf-8");

// 1. 样式表：<link rel="stylesheet" href="/_next/..."> → <style>…</style>
html = html.replace(/<link[^>]*rel="stylesheet"[^>]*href="(\/_next\/[^"]+)"[^>]*\/?>/g, (_, href) => {
  return `<style>${read(href)}</style>`;
});

// 2. 脚本：<script src="/_next/..."></script> → <script>…</script>
//    内联脚本里出现 </script> 会提前结束标签，转义成 <\/script>
html = html.replace(/<script([^>]*)\ssrc="(\/_next\/[^"]+)"([^>]*)><\/script>/g, (_, before, src, after) => {
  const attrs = `${before}${after}`.replace(/\s(async|defer)(="")?/g, "");
  const code = read(src).replace(/<\/script/gi, "<\\/script");
  return `<script${attrs}>${code}</script>`;
});

// 3. 预加载提示、图标：单文件里用不上，去掉
html = html.replace(/<link[^>]*rel="(preload|modulepreload|prefetch|icon)"[^>]*\/?>/g, "");

const leftovers = html.match(/["'(]\/_next\/[^"')]+/g) ?? [];
mkdirSync(distDir, { recursive: true });
writeFileSync(target, html);

console.log(`✓ 单文件 HTML：${path.relative(root, target)}（${(html.length / 1024).toFixed(0)} KB）`);
if (leftovers.length) {
  console.log(`  还有 ${leftovers.length} 处 /_next/ 引用（多是 RSC 数据里的路径，页面不依赖它们）：`);
  console.log("  " + [...new Set(leftovers)].slice(0, 5).join("\n  "));
}
