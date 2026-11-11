/** 学习记录：存在浏览器 localStorage 里（只在这台电脑的这个浏览器）。 */

export type StudyData = {
  version: 1;
  days: Record<string, number>; // 日期（本地）→ 当天学习秒数
  sections: Record<string, number>; // 小节 id → 累计秒数
  done: Record<string, boolean>; // 小节 id → 是否勾了「学完了」
};

const KEY = "python-notes:study";

export function emptyData(): StudyData {
  return { version: 1, days: {}, sections: {}, done: {} };
}

export function loadData(): StudyData {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return emptyData();
    const parsed = JSON.parse(raw) as Partial<StudyData>;
    return {
      version: 1,
      days: parsed.days ?? {},
      sections: parsed.sections ?? {},
      done: parsed.done ?? {},
    };
  } catch {
    return emptyData();
  }
}

export function saveData(data: StudyData): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(data));
  } catch {
    // 隐私模式或存储被禁用：只是不保存，不影响阅读
  }
}

/** 上次读到哪一节、滚到哪：下次打开可以接着读。 */
export type Reading = { id: string; y: number };
const READING_KEY = "python-notes:reading";

export function loadReading(): Reading | null {
  try {
    const raw = localStorage.getItem(READING_KEY);
    return raw ? (JSON.parse(raw) as Reading) : null;
  } catch {
    return null;
  }
}

export function saveReading(reading: Reading): void {
  try {
    localStorage.setItem(READING_KEY, JSON.stringify(reading));
  } catch {
    // 同上：存不了就算了
  }
}

/** 本地日期 YYYY-MM-DD（不用 toISOString，那是 UTC，晚上 8 点前后会跨天）。 */
export function dayKey(d: Date = new Date()): string {
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}

/** 最近 n 天的日期，从早到晚。 */
export function lastDays(n: number): string[] {
  const out: string[] = [];
  const now = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
    out.push(dayKey(d));
  }
  return out;
}

/** 连续学习天数：从今天往前数，每天至少学 1 分钟才算；今天还没学就从昨天开始数。 */
export function streak(days: Record<string, number>): number {
  const now = new Date();
  let count = 0;
  for (let i = 0; i < 3650; i++) {
    const key = dayKey(new Date(now.getFullYear(), now.getMonth(), now.getDate() - i));
    if ((days[key] ?? 0) >= 60) count++;
    else if (i === 0) continue;
    else break;
  }
  return count;
}

/** 秒 → 「1 小时 5 分」「12 分」「30 秒」。 */
export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h} 小时 ${m} 分`;
  if (m > 0) return `${m} 分`;
  return `${seconds} 秒`;
}

/** 秒 → 「01:05:09」，用在计时器上。 */
export function formatClock(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return [h, m, s].map((n) => String(n).padStart(2, "0")).join(":");
}
