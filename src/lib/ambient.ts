/**
 * 专注模式的白噪音：全部用 Web Audio 现场合成，不用音频文件（导出的单个 HTML 也能用）。
 *
 * 原理：先生成一段几秒的随机噪声循环播放，再用滤波器、音量起伏把它「调」成不同的声音。
 * - 雨声：粉红噪声去掉低频和最高频，再加上随机的雨滴声
 * - 海浪：褐噪声只留低频，音量慢慢起伏，像浪一阵一阵
 * - 白噪音：褐噪声和粉红噪声混一点，比纯白噪声柔和，像风扇声
 */

export type AmbientKind = "off" | "rain" | "waves" | "fan";

export const AMBIENT_KINDS: { kind: AmbientKind; label: string }[] = [
  { kind: "off", label: "关闭" },
  { kind: "rain", label: "雨声" },
  { kind: "waves", label: "海浪" },
  { kind: "fan", label: "白噪音" },
];

export type AmbientPrefs = { kind: AmbientKind; volume: number };

const KEY = "python-notes:ambient";
const FADE = 0.8; // 淡入淡出秒数，免得「啪」一下

export function loadAmbient(): AmbientPrefs {
  try {
    const p = JSON.parse(localStorage.getItem(KEY) ?? "{}") as Partial<AmbientPrefs>;
    const kind = AMBIENT_KINDS.some((k) => k.kind === p.kind) ? (p.kind as AmbientKind) : "off";
    const volume = typeof p.volume === "number" && p.volume >= 0 && p.volume <= 1 ? p.volume : 0.5;
    return { kind, volume };
  } catch {
    return { kind: "off", volume: 0.5 };
  }
}

export function saveAmbient(p: AmbientPrefs): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(p));
  } catch {
    // 存不了就只对这次有效
  }
}

type Color = "white" | "pink" | "brown";

function noiseBuffer(ctx: AudioContext, color: Color, seconds = 4): AudioBuffer {
  const length = ctx.sampleRate * seconds;
  const buffer = ctx.createBuffer(2, length, ctx.sampleRate);
  for (let ch = 0; ch < 2; ch++) {
    const data = buffer.getChannelData(ch);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0, last = 0;
    for (let i = 0; i < length; i++) {
      const white = Math.random() * 2 - 1;
      if (color === "white") {
        data[i] = white * 0.5;
      } else if (color === "pink") {
        // Paul Kellet 的粉红噪声近似：高频比白噪声弱，听起来不刺耳
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.969 * b2 + white * 0.153852;
        b3 = 0.8665 * b3 + white * 0.3104856;
        b4 = 0.55 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.016898;
        data[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11;
        b6 = white * 0.115926;
      } else {
        // 褐噪声：白噪声一点点累加，低频多，听起来闷、厚
        last = (last + 0.02 * white) / 1.02;
        data[i] = last * 3.5;
      }
    }
  }
  return buffer;
}

export class Ambient {
  private ctx: AudioContext | null = null;
  private master: GainNode | null = null;
  private nodes: AudioNode[] = [];
  private timers: number[] = [];
  private kind: AmbientKind = "off";
  private volume = 0.5;

  /** 切换声音；off 就淡出停止。要在点击、按键之后调用，浏览器才允许出声。 */
  play(kind: AmbientKind, volume: number): void {
    this.volume = volume;
    if (kind === this.kind) {
      this.setVolume(volume);
      return;
    }
    this.kind = kind;
    this.fadeOutAndClear();
    if (kind === "off") return;

    try {
      this.ctx ??= new AudioContext();
      void this.ctx.resume();
    } catch {
      return; // 浏览器不支持就算了
    }
    const ctx = this.ctx;
    const master = ctx.createGain();
    master.gain.setValueAtTime(0.0001, ctx.currentTime);
    master.gain.linearRampToValueAtTime(this.level(), ctx.currentTime + FADE);
    master.connect(ctx.destination);
    this.master = master;

    if (kind === "rain") this.buildRain(ctx, master);
    else if (kind === "waves") this.buildWaves(ctx, master);
    else this.buildFan(ctx, master);
  }

  setVolume(volume: number): void {
    this.volume = volume;
    if (this.ctx && this.master) this.master.gain.setTargetAtTime(this.level(), this.ctx.currentTime, 0.1);
  }

  stop(): void {
    this.kind = "off";
    this.fadeOutAndClear();
  }

  /** 离开专注模式时调用：停声音、关掉 AudioContext。 */
  dispose(): void {
    this.stop();
    const ctx = this.ctx;
    this.ctx = null;
    if (ctx) window.setTimeout(() => void ctx.close(), FADE * 1000 + 100);
  }

  /** 音量滑块是线性的，人耳听感是对数的：平方一下，小音量那头更好调。 */
  private level(): number {
    return Math.max(0.0001, this.volume * this.volume * 0.9);
  }

  private loop(ctx: AudioContext, color: Color): AudioBufferSourceNode {
    const src = ctx.createBufferSource();
    src.buffer = noiseBuffer(ctx, color);
    src.loop = true;
    src.start();
    this.nodes.push(src);
    return src;
  }

  private filter(ctx: AudioContext, type: BiquadFilterType, freq: number, q = 0.7): BiquadFilterNode {
    const f = ctx.createBiquadFilter();
    f.type = type;
    f.frequency.value = freq;
    f.Q.value = q;
    this.nodes.push(f);
    return f;
  }

  private buildRain(ctx: AudioContext, out: GainNode): void {
    // 连绵的雨声
    const hp = this.filter(ctx, "highpass", 500);
    const lp = this.filter(ctx, "lowpass", 7000);
    this.loop(ctx, "pink").connect(hp).connect(lp).connect(out);

    // 远处闷闷的底噪
    const rumble = ctx.createGain();
    rumble.gain.value = 0.35;
    this.nodes.push(rumble);
    this.loop(ctx, "brown").connect(this.filter(ctx, "lowpass", 400)).connect(rumble).connect(out);

    // 偶尔落在近处的雨滴：一小段高频噪声，快速衰减
    const dropBuffer = noiseBuffer(ctx, "white", 0.05);
    const drop = () => {
      if (!this.ctx || this.kind !== "rain") return;
      const src = ctx.createBufferSource();
      src.buffer = dropBuffer;
      const bp = ctx.createBiquadFilter();
      bp.type = "bandpass";
      bp.frequency.value = 2500 + Math.random() * 3000;
      bp.Q.value = 2;
      const g = ctx.createGain();
      const t = ctx.currentTime;
      g.gain.setValueAtTime(0.15 + Math.random() * 0.25, t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.04);
      src.connect(bp).connect(g).connect(out);
      src.start(t);
      src.stop(t + 0.05);
      this.timers.push(window.setTimeout(drop, 30 + Math.random() * 180));
    };
    drop();
  }

  private buildWaves(ctx: AudioContext, out: GainNode): void {
    const lp = this.filter(ctx, "lowpass", 900);
    const swell = ctx.createGain();
    swell.gain.value = 0.55;
    this.nodes.push(swell);
    this.loop(ctx, "brown").connect(lp).connect(swell).connect(out);

    // 一个很慢的正弦波去推音量和滤波频率：大约 9 秒一个浪
    const lfo = ctx.createOscillator();
    lfo.frequency.value = 0.11;
    const depth = ctx.createGain();
    depth.gain.value = 0.4;
    const freqDepth = ctx.createGain();
    freqDepth.gain.value = 500;
    lfo.connect(depth).connect(swell.gain);
    lfo.connect(freqDepth).connect(lp.frequency);
    lfo.start();
    this.nodes.push(lfo, depth, freqDepth);
  }

  private buildFan(ctx: AudioContext, out: GainNode): void {
    const lp = this.filter(ctx, "lowpass", 1400);
    this.loop(ctx, "brown").connect(lp).connect(out);
    const soft = ctx.createGain();
    soft.gain.value = 0.25;
    this.nodes.push(soft);
    this.loop(ctx, "pink").connect(this.filter(ctx, "lowpass", 3000)).connect(soft).connect(out);
  }

  private fadeOutAndClear(): void {
    this.timers.forEach((t) => window.clearTimeout(t));
    this.timers = [];
    const ctx = this.ctx;
    const master = this.master;
    const nodes = this.nodes;
    this.master = null;
    this.nodes = [];
    if (!ctx || !master) return;
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setValueAtTime(master.gain.value, ctx.currentTime);
    master.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + FADE);
    window.setTimeout(() => {
      nodes.forEach((n) => {
        if (n instanceof AudioScheduledSourceNode) n.stop();
        n.disconnect();
      });
      master.disconnect();
    }, FADE * 1000 + 50);
  }
}
