"use client";

import { useEffect, useRef, useState } from "react";

import { Ambient, AMBIENT_KINDS, loadAmbient, saveAmbient, type AmbientPrefs } from "@/lib/ambient";

const FOCUS_SECONDS = 25 * 60;
const BREAK_SECONDS = 5 * 60;

type Phase = "focus" | "break";

type Props = {
  /** 今天已经完成几个番茄钟。 */
  today: number;
  /** 专注满 25 分钟时调用：记一个番茄。 */
  onComplete: () => void;
  onExit: () => void;
  /** 当前是否全屏；浏览器不支持全屏（如 iPhone）时为 null，不显示按钮。 */
  fullscreen: boolean | null;
  onToggleFullscreen: () => void;
};

/** 时间到了响两声（不用音频文件，浏览器直接合成）。 */
function chime() {
  try {
    const ctx = new AudioContext();
    [0, 0.25].forEach((at, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.frequency.value = i === 0 ? 880 : 1175;
      gain.gain.setValueAtTime(0.0001, ctx.currentTime + at);
      gain.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + at + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + at + 0.5);
      osc.connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + at);
      osc.stop(ctx.currentTime + at + 0.55);
    });
    window.setTimeout(() => ctx.close(), 1200);
  } catch {
    // 没声音也不影响
  }
}

const mmss = (s: number) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

/**
 * 专注模式右上角的番茄钟：进入专注模式就开始 25 分钟倒计时，到点响铃、记一个番茄，
 * 自动进入 5 分钟休息；休息完再响一次，等你点开始下一个。
 *
 * 平时只露一个小番茄（外圈是进度，不显示数字，免得分心）；鼠标移上去才展开时间和按钮。
 * 休息中、暂停时一直展开，提醒你该干嘛。
 */
export default function FocusBar({ today, onComplete, onExit, fullscreen, onToggleFullscreen }: Props) {
  const [phase, setPhase] = useState<Phase>("focus");
  const [left, setLeft] = useState(FOCUS_SECONDS);
  const [running, setRunning] = useState(true);
  const leftRef = useRef(left);
  const onCompleteRef = useRef(onComplete);

  useEffect(() => {
    leftRef.current = left;
  }, [left]);
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  // 倒计时：按结束时刻算剩余时间，切到别的标签页（定时器变慢）也不会走慢
  useEffect(() => {
    if (!running) return;
    const endsAt = Date.now() + leftRef.current * 1000;
    const timer = window.setInterval(() => {
      const remain = Math.max(0, Math.round((endsAt - Date.now()) / 1000));
      setLeft(remain);
      if (remain > 0) return;
      window.clearInterval(timer);
      chime();
      if (phase === "focus") {
        onCompleteRef.current();
        setPhase("break");
        setLeft(BREAK_SECONDS);
        leftRef.current = BREAK_SECONDS;
      } else {
        setPhase("focus");
        setLeft(FOCUS_SECONDS);
        leftRef.current = FOCUS_SECONDS;
        setRunning(false);
      }
    }, 250);
    return () => window.clearInterval(timer);
  }, [running, phase]);

  const total = phase === "focus" ? FOCUS_SECONDS : BREAK_SECONDS;
  const progress = 1 - left / total;

  const restart = () => {
    setLeft(total);
    leftRef.current = total;
    setRunning(false);
  };

  const skipBreak = () => {
    setPhase("focus");
    setLeft(FOCUS_SECONDS);
    leftRef.current = FOCUS_SECONDS;
    setRunning(true);
  };

  // 白噪音：专注计时走着的时候才响，暂停、休息时自动停
  const ambientRef = useRef<Ambient | null>(null);
  const [ambient, setAmbient] = useState<AmbientPrefs>({ kind: "off", volume: 0.5 });
  useEffect(() => {
    ambientRef.current = new Ambient();
    // 上次选的声音存在 localStorage，只能挂载后读
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setAmbient(loadAmbient());
    return () => ambientRef.current?.dispose();
  }, []);
  const playing = phase === "focus" && running;
  useEffect(() => {
    ambientRef.current?.play(playing ? ambient.kind : "off", ambient.volume);
  }, [playing, ambient]);

  const changeAmbient = (next: AmbientPrefs) => {
    setAmbient(next);
    saveAmbient(next);
  };
  const nextKind = () => {
    const i = AMBIENT_KINDS.findIndex((k) => k.kind === ambient.kind);
    changeAmbient({ ...ambient, kind: AMBIENT_KINDS[(i + 1) % AMBIENT_KINDS.length].kind });
  };
  const ambientLabel = AMBIENT_KINDS.find((k) => k.kind === ambient.kind)?.label ?? "关闭";

  const open = phase === "break" || !running;

  return (
    <div className={`focus-bar ${phase}${open ? " open" : ""}`} role="timer" aria-label="番茄钟">
      <span className="focus-ring" style={{ "--p": progress } as React.CSSProperties} tabIndex={0}>
        {phase === "focus" ? "🍅" : "☕"}
      </span>
      <div className="focus-more">
        <span className="focus-phase">{phase === "focus" ? (running ? "专注中" : "已暂停") : "休息一下"}</span>
        <span className="focus-time">{mmss(left)}</span>

        <button type="button" onClick={() => setRunning((r) => !r)} title={running ? "暂停" : "开始"}>
          {running ? <PauseIcon /> : <PlayIcon />}
        </button>
        <button type="button" onClick={restart} title="重新开始这一轮">
          <RestartIcon />
        </button>
        {phase === "break" && (
          <button type="button" className="focus-text-btn" onClick={skipBreak}>
            跳过休息
          </button>
        )}

        <span className="focus-count" title="今天完成的番茄钟">
          今天 🍅 × {today}
        </span>
        <span className="focus-ambient">
          <button
            type="button"
            className={ambient.kind === "off" ? "" : "on"}
            onClick={nextKind}
            title="白噪音：点一下换一种（关闭 / 雨声 / 海浪 / 白噪音）"
          >
            <SoundIcon off={ambient.kind === "off"} />
            <span>{ambientLabel}</span>
          </button>
          {ambient.kind !== "off" && (
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={ambient.volume}
              onChange={(e) => changeAmbient({ ...ambient, volume: Number(e.target.value) })}
              aria-label="白噪音音量"
              title="音量"
            />
          )}
        </span>
        {fullscreen !== null && (
          <button type="button" onClick={onToggleFullscreen} title={fullscreen ? "退出全屏" : "全屏"}>
            <FullscreenIcon exit={fullscreen} />
          </button>
        )}
        <button type="button" className="focus-exit" onClick={onExit} title="退出专注模式（Esc）">
          退出专注
        </button>
      </div>
    </div>
  );
}

function SoundIcon({ off }: { off: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M4 9v6h4l5 4V5L8 9H4z" />
      {off ? <path d="M17 9l4 6M21 9l-4 6" /> : <path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12" />}
    </svg>
  );
}

function FullscreenIcon({ exit }: { exit: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {exit ? (
        <path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5" />
      ) : (
        <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />
      )}
    </svg>
  );
}

function PlayIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
      <path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.5-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z" />
    </svg>
  );
}

function PauseIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
      <rect x="6" y="5" width="4" height="14" rx="1" />
      <rect x="14" y="5" width="4" height="14" rx="1" />
    </svg>
  );
}

function RestartIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 12a9 9 0 1 0 3-6.7" />
      <path d="M3 4v5h5" />
    </svg>
  );
}
