import type { Notes } from "@/lib/notes";
import type { Reading } from "@/lib/study-store";

import Heatmap from "./Heatmap";
import type { Group } from "./NotesApp";

import "./Roadmap.css";

type Props = {
  notes: Notes;
  groups: Group[];
  done: Record<string, boolean>;
  reading: Reading | null;
  studyDays: Record<string, number>;
};

/** 首页：继续学习、学习热力图、各部分进度、12 周学习路线。 */
/** 学习路线里优先级的文字：★★★ / ★★ / ★。 */
const PRIORITY_LABEL = { 3: "必学", 2: "会用", 1: "了解" } as const;

export default function Home({ notes, groups, done, reading, studyDays }: Props) {
  const { sections, roadmap } = notes;
  const doneCount = sections.filter((s) => done[s.id]).length;
  const last = reading && sections.find((s) => s.id === reading.id);
  const firstTodo = sections.find((s) => !done[s.id]);
  const resume = last ?? firstTodo ?? sections[0];

  return (
    <div className="home">
      <header className="top">
        <h1>{notes.title}</h1>
        <div dangerouslySetInnerHTML={{ __html: notes.introHtml }} />
      </header>

      <a className="resume" href={`#${resume.id}`}>
        <span className="resume-label">{last ? "继续学习 · 上次读到" : "开始学习"}</span>
        <b>{resume.title}</b>
        <span className="resume-sub">
          已学完 {doneCount} / {sections.length} 节
          <span className="mini-bar wide">
            <i style={{ width: `${(doneCount / sections.length) * 100}%` }} />
          </span>
        </span>
        <span className="resume-go">→</span>
      </a>

      <h2 className="home-h">
        学习热力图
        <a className="home-h-link" href="#progress">
          学习过程 →
        </a>
      </h2>
      <Heatmap days={studyDays} />

      <h2 className="home-h">笔记目录</h2>
      {/* 「开始之前」这种不编号的部分只有一两节，放成一行，不占一张大卡片 */}
      {groups
        .filter((g) => g.items.every((s) => !s.num))
        .map((g) => (
          <div key={g.part} className="part-pre">
            <span className="part-pre-label">{g.part}</span>
            {g.items.map((s) => (
              <a key={s.id} href={`#${s.id}`} className={done[s.id] ? "done" : ""}>
                <span className="dot" />
                {s.title}
              </a>
            ))}
          </div>
        ))}
      <div className="part-cards">
        {groups
          .filter((g) => g.items.some((s) => s.num))
          .map((g) => {
            const n = g.items.filter((s) => done[s.id]).length;
            const todo = g.items.find((s) => !done[s.id]) ?? g.items[0];
            // 「阶段一：Python 语言基础」拆成小标签和标题两行，标题不容易折行
            const [stage, name] = g.part.includes("：") ? g.part.split("：", 2) : [null, g.part];
            return (
              <div key={g.part} className="part-card">
                <div className="part-card-head">
                  <div>
                    {stage && <span className="part-card-stage">{stage}</span>}
                    <b>{name}</b>
                  </div>
                  <span className="part-card-count">
                    {n}/{g.items.length}
                  </span>
                </div>
                <span className="mini-bar wide">
                  <i style={{ width: `${(n / g.items.length) * 100}%` }} />
                </span>
                <ul>
                  {g.items.map((s) => (
                    <li key={s.id} className={done[s.id] ? "done" : ""}>
                      <a href={`#${s.id}`}>
                        <span className="dot" />
                        <span className="sec-num">{s.num}</span>
                        <span className="part-card-name">{s.name}</span>
                      </a>
                    </li>
                  ))}
                </ul>
                <a className="part-card-go" href={`#${todo.id}`}>
                  {n === g.items.length ? "复习这部分" : n === 0 ? "开始这部分" : "接着学"}
                  <span aria-hidden>→</span>
                </a>
              </div>
            );
          })}
      </div>

      {roadmap.length > 0 && (
        <>
          <h2 className="home-h">学习路线</h2>
          <p className="hint">打勾的是笔记里已经写了的，没勾的是后面要补的内容。</p>
          <p className="prio-legend">
            <span className="prio p3">必学</span>面试必问、工作常用
            <span className="prio p2">会用</span>能上手、讲得清原理
            <span className="prio p1">了解</span>知道是什么、什么时候用，时间紧可以先跳过
          </p>
          <div className="stages">
            {roadmap.map((stage, i) => {
              const written = stage.items.filter((it) => it.done).length;
              return (
                <details key={stage.title} className="stage" open={i < 3}>
                  <summary>
                    <span className="stage-no">{i + 1}</span>
                    <span className="stage-title">{stage.title.replace(/^阶段.：/, "").replace(/（.+）$/, "")}</span>
                    <span className="stage-weeks">{stage.title.match(/（(.+)）/)?.[1]}</span>
                    <span className="stage-count">
                      已写 {written}/{stage.items.length}
                    </span>
                  </summary>
                  <ul>
                    {stage.items.map((it, j) => (
                      <li key={j} className={[it.done ? "done" : "", it.priority === 1 ? "minor" : ""].join(" ")}>
                        <span className="check">{it.done ? "✓" : ""}</span>
                        <span>
                          {it.priority && (
                            <span className={`prio p${it.priority}`}>{PRIORITY_LABEL[it.priority]}</span>
                          )}
                          <span dangerouslySetInnerHTML={{ __html: it.html }} />
                        </span>
                      </li>
                    ))}
                  </ul>
                  {stage.check && (
                    <p className="stage-check">
                      <b>验收</b>
                      <span dangerouslySetInnerHTML={{ __html: stage.check }} />
                    </p>
                  )}
                </details>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
