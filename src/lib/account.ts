/**
 * 账号和同步：登录后，学习记录会同步到后端（backend/），换电脑、换浏览器登录同一个账号，看到的是同一份进度。
 *
 * 同步发的是「增量」：上次同步之后又学了多少秒、勾了哪些「学完了」。两台电脑各学各的，后端加起来就是总时长。
 * 每批带一个 batch_id，没收到回复就原样重发，后端按 batch_id 去重，所以不会重复计时。
 */

import { emptyData, type StudyData } from "./study-store";

/** 后端地址：本地开发连本机的 uvicorn，其他情况（线上、双击打开的单文件 HTML）连线上。 */
const PROD_API = process.env.NEXT_PUBLIC_API_URL || "https://python-notes-api.vercel.app";

export function apiBase(): string {
  const host = typeof location === "undefined" ? "" : location.hostname;
  return host === "localhost" || host === "127.0.0.1" ? "http://localhost:8000" : PROD_API;
}

export type Account = { token: string; username: string };
export type Delta = Omit<StudyData, "version">;
export type SyncState = {
  claimed: boolean; // 这台电脑原有的记录是否已经传到某个账号上（只传一次）
  pending: Delta; // 还没发出去的增量
  inflight: (Delta & { batch_id: string }) | null; // 发出去了、还没收到回复的那一批
};

const AUTH_KEY = "python-notes:auth";
const SYNC_KEY = "python-notes:sync";

function read<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function write(key: string, value: unknown): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // 存不了就算了
  }
}

export const loadAccount = () => read<Account>(AUTH_KEY);
export const saveAccount = (a: Account | null) => write(AUTH_KEY, a);

export function emptyDelta(): Delta {
  const { days, sections, done, pomodoros } = emptyData();
  return { days, sections, done, pomodoros };
}

export function loadSync(): SyncState {
  const s = read<SyncState>(SYNC_KEY);
  return { claimed: s?.claimed ?? false, pending: s?.pending ?? emptyDelta(), inflight: s?.inflight ?? null };
}

export const saveSync = (s: SyncState) => write(SYNC_KEY, s);

export function isEmpty(d: Delta): boolean {
  return [d.days, d.sections, d.done, d.pomodoros].every((m) => Object.keys(m).length === 0);
}

/** 把本机已有的全部记录当成一批增量：第一次登录时传上去，和账号里已有的加在一起。 */
export function dataAsDelta(data: StudyData): Delta {
  const done = Object.fromEntries(Object.entries(data.done).filter(([, v]) => v));
  return { days: { ...data.days }, sections: { ...data.sections }, pomodoros: { ...data.pomodoros }, done };
}

function addCounts(a: Record<string, number>, b: Record<string, number>): Record<string, number> {
  const out = { ...a };
  for (const [k, v] of Object.entries(b)) out[k] = (out[k] ?? 0) + v;
  return out;
}

/** 后端返回的总数 + 请求期间本机又新增的，得到本机该显示的数据。 */
export function applyPending(server: Delta, pending: Delta): StudyData {
  return {
    version: 1,
    days: addCounts(server.days, pending.days),
    sections: addCounts(server.sections, pending.sections),
    pomodoros: addCounts(server.pomodoros, pending.pomodoros),
    done: { ...server.done, ...pending.done },
  };
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

/** 调后端接口。后端统一返回 {code, msg, data}；失败时抛出 ApiError，message 是后端给的提示。 */
export async function api<T>(path: string, body: unknown, token?: string, keepalive = false): Promise<T> {
  let res: Response;
  try {
    res = await fetch(apiBase() + path, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify(body),
      keepalive, // 关页面时也能把最后一批发出去
    });
  } catch {
    throw new ApiError(0, "连不上服务器，检查一下网络");
  }
  const json = (await res.json().catch(() => null)) as { code: number; msg: string; data: T } | null;
  if (!res.ok || !json || json.code !== 200) throw new ApiError(res.status, json?.msg ?? "服务出错了，请稍后再试");
  return json.data;
}
