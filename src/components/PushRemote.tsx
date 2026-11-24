"use client";

import { useState } from "react";

import {
  forgetPushAccount,
  loadPushAccount,
  loadPushState,
  pendingDelta,
  pushLogin,
  pushNow,
  pushTarget,
  summarize,
  type PushAccount,
} from "@/lib/push-remote";
import { formatDuration, type StudyData } from "@/lib/study-store";

import "./PushRemote.css";

/** 只在本地网站显示：本地网站平时连本机后端，学的时间要手动推到线上。 */
export function isLocalSite(): boolean {
  return typeof location !== "undefined" && (location.hostname === "localhost" || location.hostname === "127.0.0.1");
}

function describe(d: { days: number; seconds: number; done: number }): string {
  const parts = [];
  if (d.seconds > 0) parts.push(`${d.days} 天、${formatDuration(d.seconds)}`);
  if (d.done > 0) parts.push(`学完 ${d.done} 节`);
  return parts.length ? parts.join("，") : "开始日期等记录";
}

/** 账号弹窗里的「同步到线上」：登录线上账号，把本机新增的记录推上去。 */
export default function PushRemote({ data }: { data: StudyData }) {
  const [account, setAccount] = useState<PushAccount | null>(() => loadPushAccount());
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [, refresh] = useState(0);   // 推完重新算「待推送」

  const state = account ? loadPushState(account.username) : null;
  const pending = state ? summarize(state.inflight ?? pendingDelta(data, state.pushed)) : null;
  const target = pushTarget().replace(/^https?:\/\//, "");

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      setAccount(await pushLogin(username.trim(), password));
      setPassword("");
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : "登录失败" });
    } finally {
      setBusy(false);
    }
  };

  const push = async () => {
    if (!account) return;
    setBusy(true);
    setMsg(null);
    try {
      const sent = await pushNow(account, data);
      setMsg(sent ? { ok: true, text: `已同步到线上：${describe(summarize(sent))}` } : { ok: true, text: "没有新的记录，线上已经是最新的" });
      refresh((n) => n + 1);
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : "同步失败" });
      setAccount(loadPushAccount());   // 线上登录过期时 token 已被清掉，回到登录框
    } finally {
      setBusy(false);
    }
  };

  const logout = () => {
    forgetPushAccount();
    setAccount(null);
    setMsg(null);
  };

  return (
    <section className="push-remote">
      <div className="push-head">
        <b>同步到线上</b>
        <span>{target}</span>
      </div>
      <p className="push-desc">本地网站学的时间只存在本机，点一下推到线上账号；只推上次之后新增的，可以反复点。</p>

      {account ? (
        <>
          <div className="push-row">
            <span>
              线上账号 <b>{account.username}</b>
              {state?.at && <em> · 上次同步 {new Date(state.at).toLocaleString("zh-CN", { hour12: false })}</em>}
            </span>
            <button type="button" className="link-btn" onClick={logout}>
              换账号
            </button>
          </div>
          <div className="push-row">
            <span>
              待同步：{pending && (pending.days || pending.done || state?.inflight) ? describe(pending) : "没有新的记录"}
            </span>
            <button type="button" className="btn primary" onClick={() => void push()} disabled={busy}>
              {busy ? "同步中…" : "同步到线上"}
            </button>
          </div>
        </>
      ) : (
        <form className="push-login" onSubmit={login}>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="线上用户名"
            autoComplete="username"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="线上密码"
            autoComplete="current-password"
          />
          <button type="submit" className="btn primary" disabled={busy || !username.trim() || !password}>
            {busy ? "登录中…" : "登录线上账号"}
          </button>
        </form>
      )}

      {msg && <p className={`push-msg ${msg.ok ? "ok" : "err"}`}>{msg.text}</p>}
    </section>
  );
}
