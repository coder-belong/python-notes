// chat.mjs（前端写法；这里用 Node 运行：node chat.mjs）
async function chatStream(question, onText, signal) {
  const res = await fetch("http://localhost:8410/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },   // 要登录的接口再加 Authorization
    body: JSON.stringify({ question }),
    signal,                                            // 传 AbortController 的 signal，用来取消
  });
  const reader = res.body.getReader();                 // 响应体按块读，不等全部到齐
  const decoder = new TextDecoder();                   // 字节 → 文字
  let buffer = "";                                     // 一块里可能有半个事件，先攒着
  while (true) {
    const { done, value } = await reader.read();       // 读到一块
    if (done) break;                                   // 后端写完了
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");               // 按空行切成一个个事件
    buffer = events.pop();                             // 最后一段可能不完整，留到下一块
    for (const block of events) {
      const event = block.match(/^event: (.*)$/m)?.[1];
      const data = JSON.parse(block.match(/^data: (.*)$/m)?.[1] ?? "{}");
      if (event === "delta") onText(data.text);        // 拿到片段，追加到页面上
      if (event === "done") console.log("\n[完成] 共", data.length, "个字");
      if (event === "error") console.log("\n[出错]", data.msg);
    }
  }
}

// 正常使用：每来一个片段就追加显示
await chatStream("用两句话介绍 SSE", (t) => process.stdout.write(t));   // 浏览器里换成追加到页面元素

// 用户点「停止」：调 controller.abort()
const controller = new AbortController();
setTimeout(() => controller.abort(), 2000);            // 演示：2 秒后取消
try {
  await chatStream("写一篇 800 字的文章介绍 Python", (t) => process.stdout.write(t), controller.signal);
} catch (e) {
  console.log("\n[已取消]", e.name);                  // 取消会抛 AbortError
}
