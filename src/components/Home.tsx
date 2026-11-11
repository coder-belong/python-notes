import type { Notes } from "@/lib/notes";
import type { Reading } from "@/lib/study-store";

import Heatmap from "./Heatmap";
import type { Group } from "./NotesApp";

type Props = {
  notes: Notes;
  groups: Group[];
  done: Record<string, boolean>;
  reading: Reading | null;
  studyDays: Record<string, number>;
};

/** 首页：继续学习、学习热力图、各部分进度、12 周学习路线。 */
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

      <h2 className="home-h">学习热力图</h2>
      <Heatmap days={studyDays} />

      <h2 className="home-h">笔记目录</h2>
      <div className="part-cards">
        {groups.map((g) => {
          const n = g.items.filter((s) => done[s.id]).length;
          const todo = g.items.find((s) => !done[s.id]) ?? g.items[0];
          return (
            <div key={g.part} className="part-card">
              <div className="part-card-head">
                <b>{g.part}</b>
                <span>
                  {n}/{g.items.length}
                </span>
              </div>
              <span className="mini-bar wide">
                <i style={{ width: `${(n / g.items.length) * 100}%` }} />
              </span>
              <ul>
                {g.items.map((s) => (
                  <li key={s.id} className={done[s.id] ? "done" : ""}>
                    <span className="dot" />
                    <a href={`#${s.id}`}>{s.title}</a>
                  </li>
                ))}
              </ul>
              <a className="part-card-go" href={`#${todo.id}`}>
                {n === g.items.length ? "复习这部分 →" : n === 0 ? "开始这部分 →" : "接着学 →"}
              </a>
            </div>
          );
        })}
      </div>

      {roadmap.length > 0 && (
        <>
          <h2 className="home-h">学习路线</h2>
          <p className="hint">打勾的是笔记里已经写了的，没勾的是后面要补的内容；标「次要」的了解即可，时间紧可以先跳过。</p>
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
                      <li key={j} className={[it.done ? "done" : "", it.minor ? "minor" : ""].join(" ")}>
                        <span className="check">{it.done ? "✓" : ""}</span>
                        <span>
                          <span dangerouslySetInnerHTML={{ __html: it.html }} />
                          {it.minor && <span className="minor-tag">次要</span>}
                          {it.minorNote && (
                            <span className="minor-note" dangerouslySetInnerHTML={{ __html: it.minorNote }} />
                          )}
                        </span>
                      </li>
                    ))}
                  </ul>
                </details>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
