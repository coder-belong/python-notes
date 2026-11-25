"use client";

import { useCallback, useEffect, useState } from "react";

import { apiGet } from "@/lib/account";
import { dayKey, formatDuration } from "@/lib/study-store";

import "./AdminPanel.css";
import { blurActive } from "@/lib/blur";

/** 国家代码 → 中文，常见的几个；其他的原样显示。 */
const COUNTRY: Record<string, string> = { CN: "中国", HK: "中国香港", TW: "中国台湾", MO: "中国澳门", US: "美国", JP: "日本", SG: "新加坡", KR: "韩国" };

/** 地区 / IP：上面一行城市（国内只写城市「Shenzhen」，国外带上国家「Tokyo · 日本」），下面一行灰色小字的 IP。 */
function IpCell({ ip, location }: { ip: string | null; location: string | null }) {
  if (!ip) return <td className="ip dim">—</td>;
  const [city, , country] = (location ?? "").split(", ");
  const place = [city, country && country !== "CN" ? (COUNTRY[country] ?? country) : ""].filter(Boolean).join(" · ");
  return (
    <td className="ip" title={location ?? undefined}>
      <span className="ip-place">{place || "未知地区"}</span>
      <span className="ip-addr">{ip}</span>
    </td>
  );
}

type UserRow = {
  username: string;
  created_at: string | null;
  total_seconds: number;
  today_seconds: number;
  week_seconds: number;
  study_days: number;
  last_day: string | null;
  last_at: string | null; // 最近一次同步的时间（UTC），学习时每分钟同步一次
  ip: string | null; // 最近一次登录 / 同步时的 IP
  location: string | null; // IP 大概在哪：「Shenzhen, GD, CN」，线上由 Vercel 按 IP 判断
  pomodoros: number;
  done_sections: number;
};

type GuestRow = {
  id: string;
  created_at: string | null;
  total_seconds: number;
  today_seconds: number;
  last_day: string | null;
  last_at: string | null; // 最近一次上报的时间（UTC）
  became: string | null; // 后来注册 / 登录成了哪个用户
  ip: string | null; // 最近一次上报时的 IP
  location: string | null;
};

type GuestData = {
  total_guests: number;
  today_guests: number;
  converted: number;
  total_seconds: number;
  guests: GuestRow[];
};

type SortKey = "today_seconds" | "week_seconds" | "total_seconds" | "study_days" | "done_sections" | "last_day";

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: "today_seconds", label: "今天" },
  { key: "week_seconds", label: "近 7 天" },
  { key: "total_seconds", label: "累计" },
  { key: "study_days", label: "学习天数" },
  { key: "done_sections", label: "学完" },
  { key: "last_day", label: "最近学习" },
];

/** 「2026-11-12」→ 今天 / 昨天 / 3 天前 / 11-02。 */
function dayText(day: string | null, today: string): string {
  if (!day) return "还没学过";
  const diff = Math.round((Date.parse(`${today}T00:00:00`) - Date.parse(`${day}T00:00:00`)) / 86_400_000);
  if (diff <= 0) return "今天";
  if (diff === 1) return "昨天";
  if (diff < 30) return `${diff} 天前`;
  return day.slice(5);
}

const pad = (n: number) => String(n).padStart(2, "0");

/** 精确到分钟的完整时间：2026-11-13 10:21（按管理员本地时区）。 */
function dateText(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** 最近学习的时间：今天 14:32 / 昨天 09:10 / 11-12 20:05；没有精确时间时退回只显示日期。 */
function lastText(iso: string | null, day: string | null, today: string): string {
  if (!iso) return dayText(day, today);
  const d = new Date(iso);
  const time = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  const rel = dayText(dayKey(d), today);
  if (rel === "今天" || rel === "昨天") return `${rel} ${time}`;
  const sameYear = d.getFullYear() === Number(today.slice(0, 4));
  return `${sameYear ? "" : `${d.getFullYear()}-`}${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${time}`;
}

/** 管理员看所有用户的学习情况。只有管理员账号能打开，后端也会再检查一次。 */
export default function AdminPanel({ token, me, onClose }: { token: string; me: string; onClose: () => void }) {
  const [users, setUsers] = useState<UserRow[] | null>(null);
  const [guests, setGuests] = useState<GuestData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState<SortKey>("total_seconds");
  const [tab, setTab] = useState<"users" | "guests">("users"); // 下面的表格看注册用户还是访客
  const today = dayKey();

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      // 「今天」按管理员本地日期算，和每个人前端记录时用的日期一致
      const [data, guestData] = await Promise.all([
        apiGet<{ users: UserRow[] }>(`/admin/users?today=${today}`, token),
        apiGet<GuestData>(`/admin/guests?today=${today}`, token),
      ]);
      setUsers(data.users);
      setGuests(guestData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }, [token, today]);

  useEffect(() => {
    // 打开弹窗时拉一次数据，结果写进 state
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      blurActive(); // 不然打开弹窗的那个按钮会留下一圈焦点框
      onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  // 都按从大到小排；最近学习按日期字符串比较，还没学过的排最后
  const rows = [...(users ?? [])].sort((a, b) => {
    const diff =
      sort === "last_day"
        ? (b.last_at ?? b.last_day ?? "").localeCompare(a.last_at ?? a.last_day ?? "")
        : b[sort] - a[sort];
    return diff || b.total_seconds - a.total_seconds;
  });
  const list = users ?? [];
  const activeToday = list.filter((u) => u.today_seconds >= 60).length;
  const activeWeek = list.filter((u) => u.week_seconds >= 60).length;
  const allSeconds = list.reduce((a, u) => a + u.total_seconds, 0);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal stats-modal admin-modal" role="dialog" aria-label="所有用户" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>所有用户的学习情况</h3>
          <button type="button" className="link-btn admin-refresh" onClick={() => void load()} disabled={loading}>
            {loading ? "加载中…" : "刷新"}
          </button>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>

        <div className="stat-cards">
          <div className="stat-card accent">
            <span className="stat-label">今天在学</span>
            <b>
              {activeToday}
              <small> 人</small>
            </b>
            <span className="stat-sub">学了 1 分钟以上</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">近 7 天在学</span>
            <b>
              {activeWeek}
              <small> 人</small>
            </b>
            <span className="stat-sub">含今天</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">注册用户</span>
            <b>
              {list.length}
              <small> 人</small>
            </b>
            <span className="stat-sub">{list.filter((u) => u.total_seconds === 0).length} 人还没学过</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">全部用户累计</span>
            <b>{formatDuration(allSeconds)}</b>
            <span className="stat-sub">只算登录后同步上来的</span>
          </div>
        </div>

        {/* 两张表用标签切换：弹窗高度固定，只有表格区域自己滚动 */}
        <div className="admin-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={tab === "users"}
            className={tab === "users" ? "active" : ""}
            onClick={() => setTab("users")}
          >
            注册用户<span>{list.length}</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === "guests"}
            className={tab === "guests" ? "active" : ""}
            onClick={() => setTab("guests")}
          >
            访客（没登录）<span>{guests?.total_guests ?? 0}</span>
          </button>
          {tab === "guests" && guests && (
            <span className="admin-tabs-note">
              今天 {guests.today_guests} 人 · 后来注册 {guests.converted} 人 · 累计 {formatDuration(guests.total_seconds)}
            </span>
          )}
        </div>

        {tab === "users" && (
        <section className="admin-box">
          {error ? (
            <p className="account-error" role="alert">
              {error}
            </p>
          ) : users === null ? (
            <p className="hint">加载中…</p>
          ) : list.length === 0 ? (
            <p className="hint">还没有人注册。</p>
          ) : (
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>用户</th>
                    {COLUMNS.map((c) => (
                      <th key={c.key} className="num">
                        <button
                          type="button"
                          className={sort === c.key ? "active" : ""}
                          onClick={() => setSort(c.key)}
                          title={`按${c.label}排序`}
                        >
                          {c.label}
                          {sort === c.key && <span aria-hidden> ↓</span>}
                        </button>
                      </th>
                    ))}
                    <th className="num">注册于</th>
                    <th>地区 / IP</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((u) => (
                    <tr key={u.username} className={u.username === me ? "me" : ""}>
                      <td>
                        <span className="admin-user">
                          <span className="avatar">{Array.from(u.username)[0]}</span>
                          {u.username}
                          {u.username === me && <em>我</em>}
                        </span>
                      </td>
                      <td className={`num ${u.today_seconds >= 60 ? "strong" : "dim"}`}>
                        {u.today_seconds ? formatDuration(u.today_seconds) : "—"}
                      </td>
                      <td className="num">{u.week_seconds ? formatDuration(u.week_seconds) : "—"}</td>
                      <td className="num">{u.total_seconds ? formatDuration(u.total_seconds) : "—"}</td>
                      <td className="num">{u.study_days} 天</td>
                      <td className="num">{u.done_sections} 节</td>
                      <td className={`num ${u.last_day === today ? "strong" : "dim"}`}>{lastText(u.last_at, u.last_day, today)}</td>
                      <td className="num dim">{dateText(u.created_at)}</td>
                      <IpCell ip={u.ip} location={u.location} />
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
        )}

        {tab === "guests" && (
          <section className="admin-box">
            {!guests ? (
              <p className="hint">{error || "加载中…"}</p>
            ) : guests.guests.length === 0 ? (
              <p className="hint">还没有访客。</p>
            ) : (
              <div className="admin-table-wrap">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>访客</th>
                      <th className="num">今天</th>
                      <th className="num">累计</th>
                      <th className="num">最近学习</th>
                      <th className="num">首次访问</th>
                      <th>后来注册为</th>
                      <th>地区 / IP</th>
                    </tr>
                  </thead>
                  <tbody>
                    {guests.guests.map((g) => (
                      <tr key={g.id}>
                        <td className="dim" title={g.id}>
                          #{g.id.slice(-6)}
                        </td>
                        <td className={`num ${g.today_seconds >= 60 ? "strong" : "dim"}`}>
                          {g.today_seconds ? formatDuration(g.today_seconds) : "—"}
                        </td>
                        <td className="num">{g.total_seconds ? formatDuration(g.total_seconds) : "—"}</td>
                        <td className={`num ${g.last_day === today ? "strong" : "dim"}`}>{lastText(g.last_at, g.last_day, today)}</td>
                        <td className="num dim">{dateText(g.created_at)}</td>
                        <td className={g.became ? "" : "dim"}>{g.became ?? "—"}</td>
                        <IpCell ip={g.ip} location={g.location} />
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

        <div className="stats-foot">
          <span>每个人每分钟同步一次，所以这里的数字可能比本人看到的慢一两分钟。访客最多免费看 10 分钟，清掉浏览器数据会被当成新访客。</span>
        </div>
      </div>
    </div>
  );
}
