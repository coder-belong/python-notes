import "server-only";

import { readFileSync } from "node:fs";
import path from "node:path";

import hljs from "highlight.js";
import { Marked, type Token, type Tokens, type TokensList } from "marked";

export type Section = {
  id: string;
  title: string; // 完整标题，带节号：「2.5 async / await」
  num: string | null; // 节号「2.5」；「准备环境」这种不编号的是 null
  name: string; // 去掉节号的标题
  part: string | null;
  partIntroHtml: string | null; // 一个部分的第一节才有：「# 第X部分」标题下面那段导语
  html: string;
};
export type Notes = { title: string; introHtml: string; sections: Section[]; roadmap: RoadmapStage[] };

/** 学习路线（ROADMAP.md）里的一个阶段：每一项带「笔记里写没写」。 */
export type RoadmapItem = {
  done: boolean;
  html: string;
  /** 标了「（次要）」或「（次要：说明）」的项：首页显示成淡色加「次要」标签，说明放在后面。 */
  minor: boolean;
  minorNote: string | null;
};
export type RoadmapStage = { title: string; items: RoadmapItem[] };

const NOTES_PATH = path.join(process.cwd(), "content", "notes.md");
const ROADMAP_PATH = path.join(process.cwd(), "ROADMAP.md");

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

  let title = "Python 入门笔记";
  let part: string | null = null;
  const intro: Token[] = [];
  let partIntro: Token[] | null = null; // 刚进入一个新部分、还没遇到第一节时的内容
  const sections: Section[] = [];
  let current: { id: string; title: string; part: string | null; partIntro: Token[] | null; tokens: Token[] } | null =
    null;

  const flush = () => {
    if (current) {
      const nm = current.title.match(SECTION_NUM);
      sections.push({
        id: current.id,
        title: current.title,
        num: nm ? nm[1] : null,
        name: nm ? nm[2] : current.title,
        part: current.part,
        partIntroHtml: current.partIntro?.length ? render(current.partIntro) : null,
        html: render(current.tokens),
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

  return { title, introHtml: render(intro), sections, roadmap: loadRoadmap(marked) };
}

/** 行末的「（次要）」/「（次要：说明）」标记。 */
// 节号写成「阶段.第几节」：## 2.5 async / await
const SECTION_NUM = /^(\d+\.\d+)\s+(.+)$/;
const MINOR = /（次要(?:：([^）]*))?）\s*$/;

/** 读 ROADMAP.md：只取「## 阶段…」下面的勾选清单，放到首页的学习路线里。 */
function loadRoadmap(marked: Marked): RoadmapStage[] {
  const tokens = marked.lexer(readFileSync(ROADMAP_PATH, "utf-8"));
  const stages: RoadmapStage[] = [];
  let current: RoadmapStage | null = null;
  for (const token of tokens) {
    if (token.type === "heading" && (token as Tokens.Heading).depth === 2) {
      const text = (token as Tokens.Heading).text;
      current = text.startsWith("阶段") ? { title: text, items: [] } : null;
      if (current) stages.push(current);
      continue;
    }
    if (current && token.type === "list") {
      for (const item of (token as Tokens.List).items) {
        const raw = item.tokens.find((t) => t.type === "text")?.raw ?? item.text;
        const minor = raw.match(MINOR);
        const body = minor ? raw.slice(0, minor.index).trim() : raw;
        current.items.push({
          done: !!item.checked,
          html: marked.parseInline(body) as string,
          minor: !!minor,
          minorNote: minor?.[1] ? (marked.parseInline(minor[1]) as string) : null,
        });
      }
    }
  }
  return stages;
}
