"use client";

import { useEffect, useState } from "react";

import { apiGet } from "@/lib/account";
import { formatDuration } from "@/lib/study-store";
import type { useStudy } from "@/lib/use-study";

type Study = ReturnType<typeof useStudy>;

function timeText(at?: number): string {
  if (!at) return "";
  if (Date.now() - at < 60_000) return "刚刚";
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

const ICON = {
  user: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" />
    </svg>
  ),
  lock: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  ),
  eye: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ),
  eyeOff: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 3l18 18" />
      <path d="M10.6 5.1A10.6 10.6 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-3.2 4.1M6.6 6.6A17 17 0 0 0 2 12s3.6 7 10 7a9.7 9.7 0 0 0 5.4-1.6" />
      <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
    </svg>
  ),
  check: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  ),
  alert: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7.5v5.5M12 16.5v.01" />
    </svg>
  ),
  sync: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20 11a8 8 0 0 0-14.3-4.9L4 8M4 4v4h4M4 13a8 8 0 0 0 14.3 4.9L20 16M20 20v-4h-4" />
    </svg>
  ),
  team: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="9" cy="8" r="3.5" />
      <path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6" />
      <path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14.3c1.8.8 3 2.7 3 5.7" />
    </svg>
  ),
  logout: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l5-5-5-5M15 12H4" />
    </svg>
  ),
};

/** 注册页列出来的好处。 */
const PERKS = ["家里、公司登录同一个账号，进度是同一份", "学习时长、热力图、「学完了」都跟着账号走", "只要用户名和密码，不用邮箱和手机号"];

const USERNAME_RULE = /^[\p{L}\p{N}_]{2,20}$/u;

/**
 * 点开入口后的弹窗：没登录是登录 / 注册表单，登录了是账号信息和同步状态。
 * gate：访客的免费时间用完了，弹窗关不掉，注册或登录成功后才消失。
 */
export default function AccountPanel({
  study,
  onClose,
  onOpenAdmin,
  gate = false,
}: {
  study: Study;
  onClose: () => void;
  onOpenAdmin: () => void;
  gate?: boolean;
}) {
  const [mode, setMode] = useState<"login" | "register">(gate ? "register" : "login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [shaking, setShaking] = useState(false); // 出错时让输入区抖一下
  const [busy, setBusy] = useState(false);
  // 「立即同步」按钮自己的状态：本机连本机太快，转一下就结束，看不出点没点到，所以至少转 0.6 秒，再显示 2 秒结果
  const [manual, setManual] = useState<"idle" | "syncing" | "done" | "failed">("idle");
  const { account, sync, data } = study;
  // 是不是管理员由后端说了算：打开弹窗时问一次 /auth/me
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (!account) return;
    let alive = true;
    apiGet<{ is_admin?: boolean }>("/auth/me", account.token)
      .then((me) => alive && setIsAdmin(!!me.is_admin))
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, [account]);

  useEffect(() => {
    if (gate) return; // 挡住页面时 Esc 关不掉
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose, gate]);

  const syncByHand = async () => {
    setManual("syncing");
    const [ok] = await Promise.all([study.syncNow(), new Promise((r) => setTimeout(r, 600))]);
    setManual(ok ? "done" : "failed");
    setTimeout(() => setManual("idle"), 2000);
  };

  const switchMode = (m: "login" | "register") => {
    setMode(m);
    setError("");
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await study.signIn(mode, username.trim(), password);
      setPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "出错了，请稍后再试");
      setShaking(true);
    } finally {
      setBusy(false);
    }
  };

  const nameOk = USERNAME_RULE.test(username.trim());
  const passOk = password.length >= 6;
  const totalSeconds = Object.values(data.days).reduce((a, b) => a + b, 0);
  const doneCount = Object.values(data.done).filter(Boolean).length;
  const studiedDays = Object.values(data.days).filter((v) => v >= 60).length;

  return (
    <div className={`modal-backdrop pinned ${gate ? "gate" : ""}`} onClick={gate ? undefined : onClose}>
      <div className="modal account-modal" role="dialog" aria-label="账号" onClick={(e) => e.stopPropagation()}>
        {!gate && (
          <button type="button" className="modal-close account-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        )}

        {account ? (
          <div className="account-profile">
            <div className="account-hero">
              <span className="avatar big">{Array.from(account.username)[0]}</span>
              <div>
                <h3>{account.username}</h3>
                <p className={`account-sync ${sync.state}`}>
                  <span className="dot" />
                  {sync.state === "syncing" && "正在同步…"}
                  {sync.state === "ok" && `学习记录已同步 · ${timeText(sync.at)}`}
                  {sync.state === "error" && `同步失败：${sync.msg}`}
                  {sync.state === "idle" && "每分钟自动同步一次"}
                </p>
              </div>
            </div>

            <div className="account-stats">
              <div>
                <b>{formatDuration(totalSeconds)}</b>
                <span>累计学习</span>
              </div>
              <div>
                <b>{studiedDays} 天</b>
                <span>学习天数</span>
              </div>
              <div>
                <b>{doneCount} 节</b>
                <span>已学完</span>
              </div>
            </div>

            {sync.state === "error" && (
              <p className="account-note">记录先存在本机，会自动重试，不会丢。</p>
            )}

            <div className="account-actions">
              <button
                type="button"
                className={`btn primary sync-btn ${manual}`}
                onClick={() => void syncByHand()}
                disabled={manual !== "idle"}
                aria-live="polite"
              >
                <i className="btn-icon">{manual === "done" ? ICON.check : manual === "failed" ? ICON.alert : ICON.sync}</i>
                {manual === "syncing" ? "同步中…" : manual === "done" ? "已同步" : manual === "failed" ? "同步失败" : "立即同步"}
              </button>
              <button type="button" className="btn ghost" onClick={study.signOut}>
                <i className="btn-icon">{ICON.logout}</i>
                退出登录
              </button>
            </div>
            {isAdmin && (
              <button type="button" className="btn ghost wide admin-entry" onClick={onOpenAdmin}>
                <i className="btn-icon">{ICON.team}</i>
                所有用户的学习情况
                <span className="admin-badge">管理员</span>
              </button>
            )}
            <p className="account-foot">退出后本机记录还在；换台电脑登录同一个账号，进度一样。</p>
          </div>
        ) : (
          <form onSubmit={submit} className="account-form" noValidate>
            <div className="account-brand">
              <span className="account-logo">Py</span>
              <h3>{gate ? "免费阅读的 10 分钟用完了" : mode === "login" ? "欢迎回来" : "创建账号"}</h3>
              <p>
                {gate
                  ? "注册或登录后继续看，不限时间，进度还能在每台电脑上同步"
                  : mode === "login"
                    ? "登录后，学习进度在每台电脑上都一样"
                    : "注册完直接登录，本机已有的记录会一起带上"}
              </p>
            </div>

            <div className={`account-tabs ${mode}`} role="tablist">
              <span className="account-tabs-thumb" />
              {(["login", "register"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  role="tab"
                  aria-selected={mode === m}
                  className={mode === m ? "active" : ""}
                  onClick={() => switchMode(m)}
                >
                  {m === "login" ? "登录" : "注册"}
                </button>
              ))}
            </div>

            <div className={`account-fields ${shaking ? "shake" : ""}`} onAnimationEnd={() => setShaking(false)}>
              <label className="field">
                <span className="field-label">用户名</span>
                <span className="field-box">
                  <i className="field-icon">{ICON.user}</i>
                  <input
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    autoComplete="username"
                    placeholder="你的用户名"
                    maxLength={20}
                    autoFocus
                  />
                  {mode === "register" && nameOk && <i className="field-ok">{ICON.check}</i>}
                </span>
                {mode === "register" && <span className="field-help">2～20 个字，可以用字母、数字、下划线和汉字</span>}
              </label>

              <label className="field">
                <span className="field-label">密码</span>
                <span className="field-box">
                  <i className="field-icon">{ICON.lock}</i>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete={mode === "login" ? "current-password" : "new-password"}
                    placeholder={mode === "login" ? "你的密码" : "至少 6 位"}
                  />
                  <button
                    type="button"
                    className="field-eye"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? "隐藏密码" : "显示密码"}
                    title={showPassword ? "隐藏密码" : "显示密码"}
                  >
                    {showPassword ? ICON.eyeOff : ICON.eye}
                  </button>
                </span>
                {mode === "register" && (
                  <span className={`field-help ${passOk ? "ok" : ""}`}>
                    {passOk ? "密码长度可以" : `至少 6 位，还差 ${6 - password.length} 位`}
                  </span>
                )}
              </label>
            </div>

            {error && (
              <p className="account-error" role="alert">
                <i>{ICON.alert}</i>
                {error}
              </p>
            )}

            <button
              type="submit"
              className="btn primary wide"
              disabled={busy || !username.trim() || !password}
            >
              {busy && <span className="spinner" />}
              {busy ? "请稍候…" : mode === "login" ? "登录" : "注册并登录"}
            </button>

            {mode === "register" ? (
              <ul className="account-perks">
                {PERKS.map((t) => (
                  <li key={t}>
                    <i>{ICON.check}</i>
                    {t}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="account-switch">
                还没有账号？
                <button type="button" className="link-btn" onClick={() => switchMode("register")}>
                  注册一个
                </button>
              </p>
            )}
          </form>
        )}
      </div>
    </div>
  );
}
