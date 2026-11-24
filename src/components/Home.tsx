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
  onOpenProgress: () => void;
};

/** 首页：继续学习、学习热力图（旁边是「学习过程」抽屉的入口）、学习路线（每个阶段带「已写」和「已学」进度）。各节的列表在侧栏目录里，首页不再重复。 */
/** 学习路线里优先级的文字：★★★ / ★★ / ★。 */
const PRIORITY_LABEL = { 3: "必学", 2: "会用", 1: "了解" } as const;

export default function Home({ notes, groups, done, reading, studyDays, onOpenProgress }: Props) {
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
        <button type="button" className="home-h-link" onClick={onOpenProgress}>
          学习过程 →
        </button>
      </h2>
      <Heatmap days={studyDays} />

      {roadmap.length > 0 && (
        <>
          <h2 className="home-h">学习路线</h2>
          <p className="hint">「已写」是这个阶段的内容笔记里写了多少（打勾的项），「已学」是这个阶段的笔记你学完了几节。</p>
          <p className="prio-legend">
            <span className="prio p3">必学</span>面试必问、工作常用
            <span className="prio p2">会用</span>能上手、讲得清原理
            <span className="prio p1">了解</span>知道是什么、什么时候用，时间紧可以先跳过
          </p>
          <div className="stages">
            {roadmap.map((stage, i) => {
              const written = stage.items.filter((it) => it.done).length;
              // 笔记里对应的部分：按「阶段X」对上（路线标题带周数，笔记标题不带）
              const key = stage.title.split("：")[0];
              const group = groups.find((g) => g.part.split("：")[0] === key);
              const learned = group ? group.items.filter((s) => done[s.id]).length : 0;
              return (
                <details key={stage.title} className="stage" open={i < 3}>
                  <summary>
                    <span className="stage-no">{i + 1}</span>
                    <span className="stage-title">{stage.title.replace(/^阶段.：/, "").replace(/（.+）$/, "")}</span>
                    <span className="stage-weeks">{stage.title.match(/（(.+)）/)?.[1]}</span>
                    <span className="stage-count">
                      已写 {written}/{stage.items.length}
                      {group && (
                        <>
                          {" · "}
                          <span className={learned === group.items.length ? "stage-learned all" : "stage-learned"}>
                            已学 {learned}/{group.items.length} 节
                          </span>
                        </>
                      )}
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
