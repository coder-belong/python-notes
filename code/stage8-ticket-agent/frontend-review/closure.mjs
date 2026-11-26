// closure.mjs：var 和 let 在循环里的区别（闭包 + 作用域）
const a = [], b = [];
for (var i = 0; i < 3; i++) a.push(() => i);   // var：整个函数只有一个 i
for (let j = 0; j < 3; j++) b.push(() => j);   // let：每次循环一个新的 j
console.log(a.map((f) => f()), b.map((f) => f()));
