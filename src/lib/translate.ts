/**
 * AI 翻译：把一组中文片段（可以带行内 HTML）翻成英文 / 日文。
 * 按字数分成小批，同时发几批，翻好一批回调一次，页面就能一段一段换成译文，不用等整节翻完。
 * 后端按「语言 + 原文」缓存，别人翻过的直接返回；这里再加一层内存缓存，来回切换不重复请求。
 */

import { api } from "./account";
import type { Lang } from "./lang";

const BATCH_CHARS = 2500; // 一批大概多少字：几秒能翻完
const BATCH_ITEMS = 60;
const PARALLEL = 4; // 同时翻几批

const memo = new Map<string, Promise<string[]>>();

function batches(items: string[]): { start: number; items: string[] }[] {
  const out: { start: number; items: string[] }[] = [];
  let cur: string[] = [];
  let chars = 0;
  items.forEach((it, i) => {
    if (cur.length && (chars + it.length > BATCH_CHARS || cur.length >= BATCH_ITEMS)) {
      out.push({ start: i - cur.length, items: cur });
      cur = [];
      chars = 0;
    }
    cur.push(it);
    chars += it.length;
  });
  if (cur.length) out.push({ start: items.length - cur.length, items: cur });
  return out;
}

function translateBatch(items: string[], lang: Exclude<Lang, "zh">, token?: string): Promise<string[]> {
  const key = lang + "\n" + JSON.stringify(items);
  let p = memo.get(key);
  if (!p) {
    p = api<{ items: string[] }>("/ai/translate", { lang, items }, token).then((r) => r.items);
    p.catch(() => memo.delete(key)); // 失败的不缓存，下次重试
    memo.set(key, p);
  }
  return p;
}

/**
 * 翻译 items：每翻好一批调一次 onBatch(起始下标, 译文)。
 * 返回出错信息（全部成功返回 null）；cancelled() 为 true 时不再发新的批次。
 */
export async function translateItems(
  items: string[],
  lang: Exclude<Lang, "zh">,
  token: string | undefined,
  onBatch: (start: number, out: string[]) => void,
  cancelled: () => boolean,
): Promise<{ status: number; msg: string } | null> {
  const queue = batches(items);
  let error: { status: number; msg: string } | null = null;
  const worker = async () => {
    for (let b = queue.shift(); b && !cancelled() && !error; b = queue.shift()) {
      try {
        const out = await translateBatch(b.items, lang, token);
        if (!cancelled()) onBatch(b.start, out);
      } catch (e) {
        const err = e as { status?: number; message?: string };
        error = { status: err.status ?? 0, msg: err.message ?? "翻译失败" };
      }
    }
  };
  await Promise.all(Array.from({ length: PARALLEL }, worker));
  return error;
}
