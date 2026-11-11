/**
 * 以前每节的 id 是按标题生成的（比如「5-函数」），标题或编号一改，学习记录就对不上了。
 * 现在每节在 md 里写死一个固定 id（`## 5. 函数 {#functions}`），这张表把旧 id 换成新 id，
 * 浏览器里已有的「学完了」、每节用时、上次读到哪，打开页面时自动迁移过来。
 */
export const LEGACY_IDS: Record<string, string> = {
  "0-准备环境": "setup",
  "1-变量-类型-缩进": "variables",
  "2-判断和循环": "control-flow",
  "3-列表-字典-元组-集合": "collections",
  "4-推导式-一行生成列表-字典": "comprehensions",
  "5-函数": "functions",
  "6-模块和导入": "modules",
  "7-类": "classes",
  "8-dataclass-只存数据的类": "dataclass",
  "9-异常": "exceptions",
  "10-文件和-json": "files-json",
  "11-日志-环境变量-时间": "logging-env-time",
  "12-async-await": "async",
  "13-项目准备": "project-setup",
  "14-第一个接口": "first-api",
  "15-pydantic-请求体和响应格式": "pydantic",
  "16-统一响应格式和错误处理": "errors",
  "17-sqlalchemy-连数据库-用类定义表": "sqlalchemy",
  "18-session-在接口里增删改查": "session",
  "19-依赖注入-接口里拿到数据库会话": "dependency-injection",
  "20-完整的-todo-接口": "todo-api",
  "21-pytest-给接口写测试": "pytest",
};

/** 把记录里的旧 id 换成新 id；新旧都有时，用时相加、「学完了」任一为真就算。 */
export function migrateKeys<T extends number | boolean>(record: Record<string, T>): Record<string, T> {
  const out: Record<string, T> = {};
  for (const [key, value] of Object.entries(record)) {
    const id = LEGACY_IDS[key] ?? key;
    const prev = out[id];
    if (prev === undefined) out[id] = value;
    else if (typeof value === "number") out[id] = ((prev as number) + value) as T;
    else out[id] = (prev || value) as T;
  }
  return out;
}
