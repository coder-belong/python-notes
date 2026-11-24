/**
 * 本地网站（localhost）的学习记录，手动推到线上账号。
 *
 * 本地网站平时只连本机的后端，学的时间线上看不到。这里用线上已有的 POST /sync（收增量）：
 * - 本机记下「已经推上去的部分」，每次只推这之后新增的，所以可以反复点，不会重复累加
 * - 每批带 batch_id；没收到回复就原样重发同一批，后端按 batch_id 去重
 * - 线上账号的 token 单独存，和本地网站登录的账号互不影响
 */

import { ApiError, PROD_API, type Delta } from "./account";
import type { StudyData } from "./study-store";

const AUTH_KEY = "python-notes:push-auth";      // 线上账号：{ token, username }
/** 每个线上账号各记各的：{ pushed: 已推上去的累计, inflight: 发出去还没确认的那一批, at: 上次成功时间 }。退出再登录同一个账号，接着上次算，不会重推。 */
const stateKey = (username: string) => `python-notes:push-state:${username}`;
const TARGET_KEY = "python-notes:push-api";     // 只在测试时用：把推送目标换成别的后端（比如本机的 localhost:8000）

export type PushAccount = { token: string; username: string };
type PushState = { pushed: Delta; inflight: (Delta & { batch_id: string }) | null; at: string | null };

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
    // 存不了就算了：下次推送会把全部记录再算一遍
  }
}

function empty(): Delta {
  return { days: {}, sections: {}, done: {}, pomodoros: {}, started: {}, finished: {} };
}

/** 推到哪个后端：默认线上；测试时可以在控制台设 localStorage 的 python-notes:push-api。 */
export function pushTarget(): string {
  try {
    return localStorage.getItem(TARGET_KEY) || PROD_API;
  } catch {
    return PROD_API;
  }
}

export const loadPushAccount = () => read<PushAccount>(AUTH_KEY);

export function loadPushState(username: string): PushState {
  const s = read<PushState>(stateKey(username));
  return { pushed: { ...empty(), ...s?.pushed }, inflight: s?.inflight ?? null, at: s?.at ?? null };
}

/** 退出线上账号：只忘掉 token。这个账号推过哪些记录还留着，再登录同一个账号接着算。 */
export function forgetPushAccount(): void {
  write(AUTH_KEY, null);
}

async function call<T>(path: string, body: unknown, token?: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(pushTarget() + path, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "连不上线上服务器，检查一下网络");
  }
  const json = (await res.json().catch(() => null)) as { code: number; msg: string; data: T } | null;
  if (!res.ok || !json || json.code !== 200) throw new ApiError(res.status, json?.msg ?? "线上服务出错了，请稍后再试");
  return json.data;
}

/** 登录线上账号，记下 token。 */
export async function pushLogin(username: string, password: string): Promise<PushAccount> {
  const data = await call<{ token: string; username: string }>("/auth/login", { username, password });
  const account = { token: data.token, username: data.username };
  write(AUTH_KEY, account);
  return account;
}

/** 还没推上去的部分：现在的记录 - 已经推过的。 */
export function pendingDelta(data: StudyData, pushed: Delta): Delta {
  const minus = (now: Record<string, number>, sent: Record<string, number>) => {
    const out: Record<string, number> = {};
    for (const [k, v] of Object.entries(now)) {
      const d = v - (sent[k] ?? 0);
      if (d > 0) out[k] = d;
    }
    return out;
  };
  const done: Record<string, boolean> = {};
  for (const [id, v] of Object.entries(data.done)) if (v && !pushed.done[id]) done[id] = true;   // 只推「新勾上的」
  const started: Record<string, string> = {};
  for (const [id, day] of Object.entries(data.started)) if (pushed.started[id] !== day) started[id] = day;
  const finished: Record<string, string> = {};
  for (const [id, day] of Object.entries(data.finished)) {
    if (data.done[id] && pushed.finished[id] !== day) finished[id] = day;
  }
  return {
    days: minus(data.days, pushed.days),
    sections: minus(data.sections, pushed.sections),
    pomodoros: minus(data.pomodoros, pushed.pomodoros),
    done,
    started,
    finished,
  };
}

/** 一批增量的摘要：几天、多少秒、学完几节。 */
export function summarize(d: Delta): { days: number; seconds: number; done: number } {
  return {
    days: Object.keys(d.days).length,
    seconds: Object.values(d.days).reduce((a, b) => a + b, 0),
    done: Object.keys(d.done).length,
  };
}

export function isEmptyDelta(d: Delta): boolean {
  return [d.days, d.sections, d.pomodoros, d.done, d.started, d.finished].every((m) => Object.keys(m).length === 0);
}

function addInto(pushed: Delta, d: Delta): Delta {
  const add = (a: Record<string, number>, b: Record<string, number>) => {
    const out = { ...a };
    for (const [k, v] of Object.entries(b)) out[k] = (out[k] ?? 0) + v;
    return out;
  };
  return {
    days: add(pushed.days, d.days),
    sections: add(pushed.sections, d.sections),
    pomodoros: add(pushed.pomodoros, d.pomodoros),
    done: { ...pushed.done, ...d.done },
    started: { ...pushed.started, ...d.started },
    finished: { ...pushed.finished, ...d.finished },
  };
}

/**
 * 推一次。上次有没确认的一批就原样重发（同一个 batch_id，后端只算一次），否则算出新增的部分发出去。
 * 返回这次推了什么；没有新记录返回 null。
 */
export async function pushNow(account: PushAccount, data: StudyData): Promise<Delta | null> {
  const state = loadPushState(account.username);
  let batch = state.inflight;
  if (!batch) {
    const delta = pendingDelta(data, state.pushed);
    if (isEmptyDelta(delta)) return null;
    batch = { ...delta, batch_id: crypto.randomUUID().replace(/-/g, "") };
    write(stateKey(account.username), { ...state, inflight: batch });   // 先记下来：发出去没收到回复，下次重发同一批
  }
  try {
    await call("/sync", batch, account.token);
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) forgetPushAccount();   // 线上登录过期：要重新登录，没确认的那一批留着，登录后重发
    throw e;
  }
  const sent: Delta = {
    days: batch.days,
    sections: batch.sections,
    pomodoros: batch.pomodoros,
    done: batch.done,
    started: batch.started,
    finished: batch.finished,
  };
  write(stateKey(account.username), { pushed: addInto(state.pushed, sent), inflight: null, at: new Date().toISOString() });
  return sent;
}
