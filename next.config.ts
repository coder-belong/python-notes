import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 静态导出：npm run build 后生成 out/，再由 scripts/single-html.mjs 打成一个 HTML 文件
  output: "export",
};

export default nextConfig;
