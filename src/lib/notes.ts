import "server-only";

import { readFileSync } from "node:fs";
import path from "node:path";

import hljs from "highlight.js";
import { Marked, type Token, type Tokens, type TokensList } from "marked";

export type Section = {
  id: string;
  title: string; // 完整标题，带节号：「2.5 async / await」
  num: string | null; // 节号「2.5」；「阶段一导读」这种不编号的是 null
  name: string; // 去掉节号的标题
  part: string | null;
  partIntroHtml: string | null; // 一个部分的第一节才有：「# 第X部分」标题下面那段导语
  guide: boolean; // 阶段导读页（标题以「导读」结尾）：不算进「已学几节」，页末自动附上路线图里这个阶段的验收标准
  html: string;
  toc: TocItem[]; // 本节的小标题（###），右侧「本节目录」用
};
/** 一节里的一个小标题：锚点 id 和纯文字。 */
export type TocItem = { id: string; text: string };
export type Notes = {
  title: string;
  introHtml: string;
  sections: Section[];
  roadmap: RoadmapStage[];
  changelog: ChangelogDay[];
};

/** 更新日志（content/changelog.md）里的一天：一条一条的更新，每条带类型。 */
export type ChangelogEntry = { tag: string | null; html: string };
export type ChangelogDay = { date: string; entries: ChangelogEntry[] };

/** 学习路线（ROADMAP.md）里的一个阶段：每一项带「笔记里写没写」。 */
export type RoadmapItem = {
  done: boolean;
  html: string;
  /** 优先级：行首写 ★★★ / ★★ / ★。3 必学，2 会用，1 了解（首页显示成淡色）；没写是 null。 */
  priority: 1 | 2 | 3 | null;
};
/** check：这个阶段的验收标准（ROADMAP 里阶段下面「验收：」开头的那一段）。 */
export type RoadmapStage = { title: string; items: RoadmapItem[]; check: string | null };

const NOTES_PATH = path.join(process.cwd(), "content", "notes.md");
const ROADMAP_PATH = path.join(process.cwd(), "ROADMAP.md");
const CHANGELOG_PATH = path.join(process.cwd(), "content", "changelog.md");

/** 节标题末尾的固定 id：`## 5. 函数 {#functions}`。 */
const FIXED_ID = /\s*\{#([A-Za-z0-9-]+)\}\s*$/;

/** 标题 → 锚点 id：保留中文、字母、数字，其余变成连字符。 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/<[^>]+>/g, "")
    .replace(/[^\p{L}\p{N}]+/gu, "-")
    .replace(/^-+|-+$/g, "");
}

function createMarked(): Marked {
  const marked = new Marked();
  marked.use({
    gfm: true,
    renderer: {
      // 代码块：构建时就用 highlight.js 上好色，页面上不再需要高亮脚本
      code({ text, lang }) {
        const language = lang && hljs.getLanguage(lang) ? lang : "plaintext";
        const html = hljs.highlight(text, { language }).value;
        return `<pre><code class="hljs language-${language}">${html}</code></pre>\n`;
      },
      // 小标题带上锚点，方便以后链接
      heading({ tokens, depth }) {
        const text = this.parser.parseInline(tokens);
        return `<h${depth} id="${slugify(text)}">${text}</h${depth}>\n`;
      },
      // 外链新窗口打开
      link({ href, title, tokens }) {
        const text = this.parser.parseInline(tokens);
        const external = /^https?:\/\//.test(href);
        const t = title ? ` title="${title}"` : "";
        return `<a href="${href}"${t}${external ? ' target="_blank" rel="noreferrer"' : ""}>${text}</a>`;
      },
    },
  });
  return marked;
}

/** 读 content/notes.md：第一个一级标题是书名，「# 第X部分」是分组，每个二级标题是一节。 */
export function loadNotes(): Notes {
  const source = readFileSync(NOTES_PATH, "utf-8");
  const marked = createMarked();
  const tokens = marked.lexer(source);

  const render = (list: Token[]) => {
    const group = list as TokensList;
    group.links = tokens.links;
    return marked.parser(group);
  };

  let title = "AI 应用开发笔记";
  let part: string | null = null;
  const intro: Token[] = [];
  let partIntro: Token[] | null = null; // 刚进入一个新部分、还没遇到第一节时的内容
  const sections: Section[] = [];
  const roadmap = loadRoadmap(marked);
  let current: { id: string; title: string; part: string | null; partIntro: Token[] | null; tokens: Token[] } | null =
    null;

  const flush = () => {
    if (current) {
      const nm = current.title.match(SECTION_NUM);
      const guide = current.title.endsWith("导读");
      let body = render(current.tokens);
      if (guide) {
        // 验收标准只写在 ROADMAP.md 里一份：按「阶段X」对上，附在导读最后
        const key = (current.part ?? "").split("：")[0];
        const check = roadmap.find((st) => st.title.split("：")[0] === key)?.check;
        if (check) body += `<h3 id="验收">验收</h3>\n<p>${check}</p>\n<p class="hint">学完这个阶段，回来对照这一条自测：做得到再进下一阶段。</p>\n`;
      }
      const { html, toc } = collectToc(body);
      sections.push({
        id: current.id,
        title: current.title,
        num: nm ? nm[1] : null,
        name: nm ? nm[2] : current.title,
        part: current.part,
        partIntroHtml: current.partIntro?.length ? render(current.partIntro) : null,
        guide,
        html,
        toc,
      });
    }
  };

  let seenTitle = false;
  for (const token of tokens) {
    if (token.type === "hr") continue; // 分隔线由节与节之间的间距代替
    if (token.type === "heading") {
      const h = token as Tokens.Heading;
      if (h.depth === 1) {
        if (!seenTitle) {
          title = h.text;
          seenTitle = true;
        } else {
          flush();
          current = null;
          part = h.text;
          partIntro = [];
        }
        continue;
      }
      if (h.depth === 2) {
        flush();
        // 每节的 id 写死在标题后面，改标题、改编号都不影响学习记录；没写就按标题生成
        const m = h.text.match(FIXED_ID);
        const sectionTitle = m ? h.text.slice(0, m.index).trim() : h.text;
        current = { id: m ? m[1] : slugify(sectionTitle), title: sectionTitle, part, partIntro, tokens: [] };
        partIntro = null;
        continue;
      }
    }
    if (current) current.tokens.push(token);
    else if (partIntro) partIntro.push(token);
    else intro.push(token);
  }
  flush();

  return { title, introHtml: render(intro), sections, roadmap, changelog: loadChangelog(marked) };
}

/**
 * 从一节的 HTML 里取出所有 <h3> 做目录。同一节里重名的小标题，id 后面加 -2、-3，保证点击能跳到对的那个。
 */
function collectToc(html: string): { html: string; toc: TocItem[] } {
  const toc: TocItem[] = [];
  const used = new Map<string, number>();
  const out = html.replace(/<h3 id="([^"]*)">([\s\S]*?)<\/h3>/g, (_, rawId: string, inner: string) => {
    const base = rawId || "h";
    const n = (used.get(base) ?? 0) + 1;
    used.set(base, n);
    const id = n === 1 ? base : `${base}-${n}`;
    const text = inner
      .replace(/<[^>]+>/g, "")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&amp;/g, "&");
    toc.push({ id, text });
    return `<h3 id="${id}">${inner}</h3>`;
  });
  return { html: out, toc };
}

// 节号写成「阶段.第几节」：## 2.5 async / await
const SECTION_NUM = /^(\d+\.\d+)\s+(.+)$/;
/** 行首的优先级：★★★ 必学、★★ 会用、★ 了解。 */
const PRIORITY = /^(★{1,3})\s*/;
/** 阶段下面的验收标准：「验收：……」 */
const CHECK = /^验收：\s*/;

/** 读 ROADMAP.md：只取「## 阶段…」下面的勾选清单，放到首页的学习路线里。 */
function loadRoadmap(marked: Marked): RoadmapStage[] {
  const tokens = marked.lexer(readFileSync(ROADMAP_PATH, "utf-8"));
  const stages: RoadmapStage[] = [];
  let current: RoadmapStage | null = null;
  for (const token of tokens) {
    if (token.type === "heading" && (token as Tokens.Heading).depth === 2) {
      const text = (token as Tokens.Heading).text;
      current = text.startsWith("阶段") ? { title: text, items: [], check: null } : null;
      if (current) stages.push(current);
      continue;
    }
    if (current && token.type === "paragraph" && CHECK.test((token as Tokens.Paragraph).text)) {
      current.check = marked.parseInline((token as Tokens.Paragraph).text.replace(CHECK, "")) as string;
      continue;
    }
    if (current && token.type === "list") {
      for (const item of (token as Tokens.List).items) {
        const raw = item.tokens.find((t) => t.type === "text")?.raw ?? item.text;
        const star = raw.match(PRIORITY);
        current.items.push({
          done: !!item.checked,
          html: marked.parseInline(star ? raw.slice(star[0].length) : raw) as string,
          priority: star ? (star[1].length as 1 | 2 | 3) : null,
        });
      }
    }
  }
  return stages;
}

/** 每条更新开头的类型：【新功能】【改进】【笔记】【修复】。 */
const CHANGELOG_TAG = /^【([^】]+)】\s*/;

/** 读 content/changelog.md：每个「## 日期」是一天，下面的列表是这天的更新。 */
function loadChangelog(marked: Marked): ChangelogDay[] {
  const tokens = marked.lexer(readFileSync(CHANGELOG_PATH, "utf-8"));
  const days: ChangelogDay[] = [];
  for (const token of tokens) {
    if (token.type === "heading" && (token as Tokens.Heading).depth === 2) {
      days.push({ date: (token as Tokens.Heading).text.trim(), entries: [] });
      continue;
    }
    const day = days[days.length - 1];
    if (day && token.type === "list") {
      for (const item of (token as Tokens.List).items) {
        const raw = item.text.trim();
        const tag = raw.match(CHANGELOG_TAG);
        day.entries.push({
          tag: tag ? tag[1] : null,
          html: marked.parseInline(tag ? raw.slice(tag[0].length) : raw) as string,
        });
      }
    }
  }
  return days;
}
