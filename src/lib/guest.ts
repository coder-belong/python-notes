/**
 * 访客（没登录）：只能免费看 10 分钟，用完要注册或登录。
 *
 * 时长和登录后的学习时长是同一个计法（页面在前台、最近 90 秒有操作才算），单独存一份，
 * 每天的总秒数会上报给后端，管理员能看到访客学了多久。
 *
 * 限制只在前端：清掉浏览器数据或开无痕窗口就能重新计时。这是提醒注册的门槛，不是防破解的锁。
 */

import { api } from "./account";

/** 访客能免费看多少秒。 */
export const GUEST_LIMIT = 10 * 60;

export type GuestState = {
  id: string; // 随机生成，后端用它区分不同访客
  days: Record<string, number>; // 日期（本地）→ 当天以访客身份学了多少秒
};

const KEY = "python-notes:guest";

function newId(): string {
  // 后端要求 12～32 位小写字母和数字
  return (Date.now().toString(36) + Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2)).slice(0, 24);
}

export function loadGuest(): GuestState {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const g = JSON.parse(raw) as Partial<GuestState>;
      if (g.id && /^[a-z0-9]{12,32}$/.test(g.id)) return { id: g.id, days: g.days ?? {} };
    }
  } catch {
    // 读不到就当新访客
  }
  const fresh = { id: newId(), days: {} };
  saveGuest(fresh);
  return fresh;
}

export function saveGuest(g: GuestState): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(g));
  } catch {
    // 存不了就算了：刷新后会重新计时
  }
}

export function guestSeconds(g: GuestState): number {
  return Object.values(g.days).reduce((a, b) => a + b, 0);
}

/** 上报最近 31 天的每日总秒数（后端取较大值，重复发不会多算）。keepalive：关页面时也能发出去。 */
export function reportGuest(g: GuestState, keepalive = false): Promise<unknown> {
  const days = Object.fromEntries(
    Object.entries(g.days)
      .sort(([a], [b]) => b.localeCompare(a))
      .slice(0, 31),
  );
  return api("/guest/sync", { guest_id: g.id, days }, undefined, keepalive).catch(() => {});
}
