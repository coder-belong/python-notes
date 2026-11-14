"use client";

import { useCallback, useEffect, useState } from "react";

import { apiGet } from "@/lib/account";
import { dayKey, formatDuration } from "@/lib/study-store";

type UserRow = {
  username: string;
  created_at: string | null;
  total_seconds: number;
  today_seconds: number;
  week_seconds: number;
  study_days: number;
  last_day: string | null;
  pomodoros: number;
  done_sections: number;
};

type GuestRow = {
  id: string;
  created_at: string | null;
  total_seconds: number;
  today_seconds: number;
  last_day: string | null;
  became: string | null; // 后来注册 / 登录成了哪个用户
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

function dateText(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** 管理员看所有用户的学习情况。只有管理员账号能打开，后端也会再检查一次。 */
export default function AdminPanel({ token, me, onClose }: { token: string; me: string; onClose: () => void }) {
  const [users, setUsers] = useState<UserRow[] | null>(null);
  const [guests, setGuests] = useState<GuestData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState<SortKey>("total_seconds");
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
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  // 都按从大到小排；最近学习按日期字符串比较，还没学过的排最后
  const rows = [...(users ?? [])].sort((a, b) => {
    const diff =
      sort === "last_day" ? (b.last_day ?? "").localeCompare(a.last_day ?? "") : b[sort] - a[sort];
    return diff || b.total_seconds - a.total_seconds;
  });
  const list = users ?? [];
  const activeToday = list.filter((u) => u.today_seconds >= 60).length;
  const activeWeek = list.filter((u) => u.week_seconds >= 60).length;
  const allSeconds = list.reduce((a, u) => a + u.total_seconds, 0);
  const weekMax = Math.max(60, ...list.map((u) => u.week_seconds));

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

        <section className="stats-box admin-box">
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
                      <td className="num">
                        <span className="admin-week">
                          <span className="admin-bar">
                            <i style={{ width: `${(u.week_seconds / weekMax) * 100}%` }} />
                          </span>
                          {u.week_seconds ? formatDuration(u.week_seconds) : "—"}
                        </span>
                      </td>
                      <td className="num">{u.total_seconds ? formatDuration(u.total_seconds) : "—"}</td>
                      <td className="num">{u.study_days} 天</td>
                      <td className="num">{u.done_sections} 节</td>
                      <td className={`num ${u.last_day === today ? "strong" : "dim"}`}>{dayText(u.last_day, today)}</td>
                      <td className="num dim">{dateText(u.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>


        {guests && (
          <section className="stats-box admin-box admin-guests">
            <div className="admin-guests-head">
              <h4>访客（没登录）</h4>
              <span>
                共 {guests.total_guests} 人 · 今天 {guests.today_guests} 人 · 后来注册 {guests.converted} 人 · 累计{" "}
                {formatDuration(guests.total_seconds)}
              </span>
            </div>
            {guests.guests.length === 0 ? (
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
                        <td className={`num ${g.last_day === today ? "strong" : "dim"}`}>{dayText(g.last_day, today)}</td>
                        <td className="num dim">{dateText(g.created_at)}</td>
                        <td className={g.became ? "" : "dim"}>{g.became ?? "—"}</td>
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
