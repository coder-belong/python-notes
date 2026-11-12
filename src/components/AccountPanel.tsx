"use client";

import { useEffect, useState } from "react";

import type { useStudy } from "@/lib/use-study";

type Study = ReturnType<typeof useStudy>;

function timeText(at?: number): string {
  if (!at) return "";
  const d = new Date(at);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

/** 侧栏顶部的账号按钮：没登录是人像图标；登录后显示用户名的第一个字，右下角小点表示同步状态。 */
export function AccountEntry({ study, onOpen }: { study: Study; onOpen: () => void }) {
  const { account, sync } = study;
  const status =
    sync.state === "syncing"
      ? "同步中"
      : sync.state === "error"
        ? "同步失败"
        : sync.state === "ok"
          ? `已同步 ${timeText(sync.at)}`
          : "";
  const label = account ? `${account.username}${status ? ` · ${status}` : ""}` : "登录 / 注册：登录后多台电脑同步进度";
  return (
    <button
      type="button"
      className={`icon-btn account-btn ${account ? "in" : ""} ${sync.state}`}
      onClick={onOpen}
      aria-label={label}
      title={label}
    >
      {account ? (
        <span className="avatar">{Array.from(account.username)[0]}</span>
      ) : (
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" strokeWidth="2" />
          <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      )}
      {account && <span className="sync-dot" />}
    </button>
  );
}

/** 点开入口后的弹窗：没登录是登录 / 注册表单，登录了是同步状态和退出。 */
export default function AccountPanel({ study, onClose }: { study: Study; onClose: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { account, sync } = study;

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await study.signIn(mode, username.trim(), password);
      setPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "出错了，请稍后再试");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal account-modal" role="dialog" aria-label="账号" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>{account ? "账号" : mode === "login" ? "登录" : "注册"}</h3>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>

        {account ? (
          <>
            <p className="account-hello">
              已登录：<b>{account.username}</b>
            </p>
            <p className={`account-sync ${sync.state}`}>
              {sync.state === "syncing" && "正在同步…"}
              {sync.state === "ok" && `学习记录已同步（${timeText(sync.at)}）`}
              {sync.state === "error" && `同步失败：${sync.msg}。记录先存在本机，稍后会自动重试。`}
              {sync.state === "idle" && "登录后每分钟自动同步一次。"}
            </p>
            <div className="account-actions">
              <button type="button" className="btn primary" onClick={() => void study.syncNow()}>
                立即同步
              </button>
              <button type="button" className="btn" onClick={study.signOut}>
                退出登录
              </button>
            </div>
            <p className="hint">退出登录后，这台电脑上的记录还在；在别的电脑登录同一个账号，能看到同样的进度。</p>
          </>
        ) : (
          <form onSubmit={submit} className="account-form">
            <div className="account-tabs" role="tablist">
              {(["login", "register"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  role="tab"
                  aria-selected={mode === m}
                  className={mode === m ? "active" : ""}
                  onClick={() => {
                    setMode(m);
                    setError("");
                  }}
                >
                  {m === "login" ? "登录" : "注册"}
                </button>
              ))}
            </div>
            <label>
              <span>用户名</span>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                placeholder="2～20 个字：字母、数字、下划线、汉字"
                required
                autoFocus
              />
            </label>
            <label>
              <span>密码</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                placeholder="至少 6 位"
                required
              />
            </label>
            {error && <p className="account-error">{error}</p>}
            <button type="submit" className="btn primary wide" disabled={busy}>
              {busy ? "请稍候…" : mode === "login" ? "登录" : "注册并登录"}
            </button>
            <p className="hint">
              登录后，这台电脑上已有的学习记录会合并到账号里；家里、公司登录同一个账号，进度是同一份。
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
