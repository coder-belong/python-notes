"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  api,
  ApiError,
  applyPending,
  dataAsDelta,
  emptyDelta,
  isEmpty,
  loadAccount,
  loadSync,
  saveAccount,
  saveSync,
  type Account,
  type Delta,
  type SyncState,
} from "./account";
import { GUEST_LIMIT, guestSeconds, loadGuest, reportGuest, saveGuest, type GuestState } from "./guest";
import { dayKey, emptyData, loadData, saveData, type StudyData } from "./study-store";

/** 每批同步的随机 id（双击打开的 HTML 里 crypto.randomUUID 不一定能用，自己拼一个）。 */
function randomId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 12);
}

/** 多久没操作就暂停计时。 */
const IDLE_SECONDS = 90;
/** 多久写一次 localStorage。 */
const SAVE_EVERY = 10;
/** 登录后多久同步一次。 */
const SYNC_EVERY = 60;

export type StudyStatus = "studying" | "idle" | "hidden";
export type SyncStatus = { state: "idle" | "syncing" | "ok" | "error"; at?: number; msg?: string };

/**
 * 在线学习时长：页面在前台、窗口有焦点、并且最近 90 秒内有过滚动 / 鼠标 / 键盘操作时，每秒记 1 秒，
 * 同时记到「今天」和「当前读到的小节」上。切到别的标签页、离开电脑都会自动暂停。
 *
 * 登录后每分钟、切走页面时，把新增的记录同步到账号上（见 account.ts）。
 */
export function useStudy(currentSection: string | null) {
  const [data, setData] = useState<StudyData>(emptyData);
  const [loaded, setLoaded] = useState(false);
  const [sessionSeconds, setSessionSeconds] = useState(0);
  const [status, setStatus] = useState<StudyStatus>("studying");
  const [account, setAccount] = useState<Account | null>(null);
  const [sync, setSync] = useState<SyncStatus>({ state: "idle" });
  const [guestSecs, setGuestSecs] = useState(0); // 没登录时，以访客身份已经看了多少秒

  const dataRef = useRef<StudyData>(data);
  const syncRef = useRef<SyncState>({ claimed: false, pending: emptyDelta(), inflight: null });
  const accountRef = useRef<Account | null>(null);
  const syncingRef = useRef(false);
  const sectionRef = useRef<string | null>(currentSection);
  const lastActiveRef = useRef<number>(0);
  const unsavedRef = useRef(0);
  const guestRef = useRef<GuestState | null>(null);

  useEffect(() => {
    sectionRef.current = currentSection;
  }, [currentSection]);

  // 首次进入：读出保存的记录（只能在浏览器里读 localStorage）
  useEffect(() => {
    const saved = loadData();
    dataRef.current = saved;
    syncRef.current = loadSync();
    accountRef.current = loadAccount();
    guestRef.current = loadGuest();
    lastActiveRef.current = Date.now();
    // 读 localStorage 只能放在 effect 里，读完再同步到 state
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setData(saved);
    setAccount(accountRef.current);
    setGuestSecs(guestSeconds(guestRef.current));
    setLoaded(true);
  }, []);

  const flush = useCallback(() => {
    saveData(dataRef.current);
    saveSync(syncRef.current);
    if (guestRef.current) saveGuest(guestRef.current);
    unsavedRef.current = 0;
  }, []);

  const commit = useCallback((updated: StudyData, change: (p: Delta) => void) => {
    dataRef.current = updated;
    change(syncRef.current.pending);
    setData(updated);
  }, []);

  const setLoggedIn = useCallback((a: Account | null) => {
    accountRef.current = a;
    saveAccount(a);
    setAccount(a);
  }, []);

  /**
   * 同步一次：把还没发的增量发给后端，拿回账号的全部记录。
   * keepalive：关页面时用，发出去就不管回复了；没确认的那批下次打开会用同一个 batch_id 重发。
   * 返回这次同步是否成功（正在同步时再点，算成功：那一次会把最新数据带回来）。
   */
  const syncNow = useCallback(
    async (keepalive = false): Promise<boolean> => {
      const acc = accountRef.current;
      if (!acc) return false;
      if (syncingRef.current) return true;
      const st = syncRef.current;
      // 这台电脑第一次登录：本机原有的记录整个当成增量传上去（之后的增量都已经算在里面了）
      if (!st.claimed) {
        st.pending = dataAsDelta(dataRef.current);
        st.claimed = true;
      }
      if (!st.inflight) {
        st.inflight = { ...st.pending, batch_id: randomId() };
        st.pending = emptyDelta();
      }
      saveSync(st);
      const batch = st.inflight;

      if (keepalive) {
        if (!isEmpty(batch)) api("/sync", batch, acc.token, true).catch(() => {});
        return true;
      }

      syncingRef.current = true;
      setSync((s) => ({ ...s, state: "syncing" }));
      try {
        const server = await api<Delta>("/sync", batch, acc.token);
        if (accountRef.current !== acc) return false; // 请求期间退出了登录
        st.inflight = null;
        const merged = applyPending(server, st.pending);
        dataRef.current = merged;
        setData(merged);
        flush();
        setSync({ state: "ok", at: Date.now() });
        return true;
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) {
          setLoggedIn(null); // token 过期或无效：退出登录，记录留在本机，下次登录接着传
          setSync({ state: "error", msg: e.message });
        } else {
          setSync({ state: "error", at: Date.now(), msg: e instanceof Error ? e.message : "同步失败" });
        }
        return false;
      } finally {
        syncingRef.current = false;
      }
    },
    [flush, setLoggedIn],
  );

  /** 登录或注册。注册成功后端直接返回 token，等于已经登录。 */
  const signIn = useCallback(
    async (mode: "login" | "register", username: string, password: string) => {
      // 没登录时带上访客 id，后端记下「这个访客后来注册 / 登录了」
      const guest_id = accountRef.current ? undefined : guestRef.current?.id;
      const a = await api<Account>(`/auth/${mode}`, { username, password, guest_id });
      setLoggedIn(a);
      await syncNow();
    },
    [setLoggedIn, syncNow],
  );

  /** 退出登录：本机的记录保留，不会删。 */
  const signOut = useCallback(() => {
    void syncNow(true); // 走之前把没发的发出去
    setLoggedIn(null);
    setSync({ state: "idle" });
  }, [setLoggedIn, syncNow]);

  // 打开页面先同步一次，之后每分钟一次
  useEffect(() => {
    if (!loaded || !account) return;
    // 同步要发请求，只能放在 effect 里；它会更新同步状态
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void syncNow();
    const timer = window.setInterval(() => void syncNow(), SYNC_EVERY * 1000);
    return () => window.clearInterval(timer);
  }, [loaded, account, syncNow]);

  // 没登录：每分钟把访客的学习时长报给后端（管理员能看到）
  useEffect(() => {
    if (!loaded || account) return;
    const report = () => {
      const g = guestRef.current;
      if (g && guestSeconds(g) > 0) void reportGuest(g);
    };
    report();
    const timer = window.setInterval(report, SYNC_EVERY * 1000);
    return () => window.clearInterval(timer);
  }, [loaded, account]);

  // 记录用户操作，判断是否在学
  useEffect(() => {
    const markActive = () => {
      lastActiveRef.current = Date.now();
    };
    const events = ["mousemove", "mousedown", "keydown", "scroll", "wheel", "touchstart"] as const;
    events.forEach((e) => window.addEventListener(e, markActive, { passive: true }));
    const onHide = () => {
      if (document.visibilityState === "hidden") {
        flush();
        void syncNow(true);
        const g = guestRef.current;
        if (!accountRef.current && g && guestSeconds(g) > 0) void reportGuest(g, true);
      } else markActive();
    };
    document.addEventListener("visibilitychange", onHide);
    window.addEventListener("pagehide", flush);
    return () => {
      events.forEach((e) => window.removeEventListener(e, markActive));
      document.removeEventListener("visibilitychange", onHide);
      window.removeEventListener("pagehide", flush);
    };
  }, [flush, syncNow]);

  // 每秒判断一次：在学就加 1 秒
  useEffect(() => {
    if (!loaded) return;
    const timer = window.setInterval(() => {
      const visible = document.visibilityState === "visible" && document.hasFocus();
      const recent = Date.now() - lastActiveRef.current < IDLE_SECONDS * 1000;
      const next: StudyStatus = !visible ? "hidden" : recent ? "studying" : "idle";
      setStatus(next);
      if (next !== "studying") return;

      const today = dayKey();
      // 没登录：记到访客时长上；10 分钟用完就不再计时（页面被挡住了）
      const guest = guestRef.current;
      if (!accountRef.current && guest) {
        if (guestSeconds(guest) >= GUEST_LIMIT) return;
        guest.days[today] = (guest.days[today] ?? 0) + 1;
        setGuestSecs((s) => s + 1);
      }

      const prev = dataRef.current;
      const section = sectionRef.current;
      const updated: StudyData = {
        ...prev,
        days: { ...prev.days, [today]: (prev.days[today] ?? 0) + 1 },
        sections: section ? { ...prev.sections, [section]: (prev.sections[section] ?? 0) + 1 } : prev.sections,
      };
      commit(updated, (p) => {
        p.days[today] = (p.days[today] ?? 0) + 1;
        if (section) p.sections[section] = (p.sections[section] ?? 0) + 1;
      });
      setSessionSeconds((s) => s + 1);

      unsavedRef.current += 1;
      if (unsavedRef.current >= SAVE_EVERY) flush();
    }, 1000);
    return () => window.clearInterval(timer);
  }, [loaded, flush, commit]);

  const toggleDone = useCallback(
    (id: string) => {
      const prev = dataRef.current;
      const value = !prev.done[id];
      commit({ ...prev, done: { ...prev.done, [id]: value } }, (p) => {
        p.done[id] = value;
      });
      flush();
      void syncNow(); // 勾选马上同步，不等一分钟
    },
    [flush, commit, syncNow],
  );

  /** 专注模式里完成一个番茄钟：记到今天。 */
  const addPomodoro = useCallback(() => {
    const prev = dataRef.current;
    const today = dayKey();
    commit({ ...prev, pomodoros: { ...prev.pomodoros, [today]: (prev.pomodoros[today] ?? 0) + 1 } }, (p) => {
      p.pomodoros[today] = (p.pomodoros[today] ?? 0) + 1;
    });
    flush();
  }, [flush, commit]);

  /** 清空本机记录（只在没登录时提供：登录后账号里的记录还在，下次同步又会回来）。 */
  const reset = useCallback(() => {
    const fresh = emptyData();
    dataRef.current = fresh;
    syncRef.current = { claimed: false, pending: emptyDelta(), inflight: null };
    setData(fresh);
    setSessionSeconds(0);
    flush();
  }, [flush]);

  return {
    data,
    loaded,
    sessionSeconds,
    status,
    toggleDone,
    addPomodoro,
    reset,
    account,
    sync,
    syncNow,
    signIn,
    signOut,
    guestSeconds: guestSecs,
    /** 没登录、免费的 10 分钟用完了：要注册或登录才能继续看。 */
    guestBlocked: loaded && !account && guestSecs >= GUEST_LIMIT,
  };
}
