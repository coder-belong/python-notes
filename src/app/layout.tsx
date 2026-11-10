import { readFileSync } from "node:fs";
import path from "node:path";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Python 入门笔记",
  description: "基础语法 → FastAPI 写接口 → SQLAlchemy 连数据库 → pytest 测试",
};

// 样式在构建时直接写进页面：打成单个 HTML 后不再依赖 /_next/ 下的 CSS 文件
// （用 import "./globals.css" 的话，React 运行时还会按路径去加载一次 CSS，单文件里会 404）
const css = readFileSync(path.join(process.cwd(), "src", "styles", "globals.css"), "utf-8");

// 不用 next/font：字体文件同样走 /_next/ 路径，单文件里加载不到，直接用系统字体
export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="zh-CN">
      <head>
        <style dangerouslySetInnerHTML={{ __html: css }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
