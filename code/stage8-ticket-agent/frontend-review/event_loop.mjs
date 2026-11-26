// event_loop.mjs：面试最常考的执行顺序：同步代码 → 微任务（Promise）→ 宏任务（setTimeout）
console.log("1 同步");
setTimeout(() => console.log("7 宏任务 setTimeout"), 0);
Promise.resolve().then(() => console.log("4 微任务 then"));
queueMicrotask(() => console.log("5 微任务 queueMicrotask"));
(async () => {
  console.log("2 async 函数里 await 之前：同步执行");
  await null;
  console.log("6 await 之后：排在前面两个微任务后面");
})();
console.log("3 同步");
