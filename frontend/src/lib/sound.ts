/**
 * Sound manager using Howler.js. PLAN §20.
 *
 * Friendly space cockpit audio: soft beeps, warm synths, real NASA clips.
 * Respects system silent mode and user preferences.
 *
 * Sound files are loaded lazily on first interaction (browsers require
 * user gesture before audio can play). Placeholders use Web Audio API
 * synthesized tones until real audio assets are added.
 */
"use client";

type SoundCategory = "sfx" | "music" | "voice";

type SoundSettings = {
  master: number;   // 0-1
  sfx: number;      // 0-1
  music: number;    // 0-1
  voice: number;    // 0-1
  muted: boolean;
};

const STORAGE_KEY = "nse:sound:v1";

const DEFAULT_SETTINGS: SoundSettings = {
  master: 0.7,
  sfx: 0.7,
  music: 0.3,
  voice: 1.0,
  muted: false,
};

let settings: SoundSettings = { ...DEFAULT_SETTINGS };
let audioCtx: AudioContext | null = null;
let initialized = false;

function loadSettings(): SoundSettings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch { /* ignore */ }
  return DEFAULT_SETTINGS;
}

function saveSettings(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch { /* ignore */ }
}

function getCtx(): AudioContext {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
  }
  return audioCtx;
}

function effectiveVolume(category: SoundCategory): number {
  if (settings.muted) return 0;
  return settings.master * settings[category];
}

/**
 * Play a synthesized tone. Used as placeholder until real audio assets are added.
 * Frequencies chosen to match the "soft sine-wave blip" and "ascending chime"
 * descriptions in PLAN §20.2.
 */
function playTone(freq: number, duration: number, category: SoundCategory, type: OscillatorType = "sine"): void {
  const vol = effectiveVolume(category);
  if (vol === 0) return;
  try {
    const ctx = getCtx();
    if (ctx.state === "suspended") ctx.resume();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(vol * 0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + duration);
  } catch { /* audio not available */ }
}

// --- Public API ---

export const SoundManager = {
  init(): void {
    if (initialized) return;
    settings = loadSettings();
    initialized = true;
  },

  getSettings(): SoundSettings {
    return { ...settings };
  },

  updateSettings(partial: Partial<SoundSettings>): void {
    settings = { ...settings, ...partial };
    saveSettings();
  },

  toggleMute(): boolean {
    settings.muted = !settings.muted;
    saveSettings();
    return settings.muted;
  },

  // UI sound effects (§20.2)
  click(): void { playTone(880, 0.08, "sfx"); },
  hover(): void { playTone(1200, 0.04, "sfx"); },
  transition(): void { playTone(440, 0.2, "sfx", "triangle"); },
  error(): void { playTone(220, 0.25, "sfx", "triangle"); },

  // Game feedback (§20.2)
  correct(): void {
    // Ascending 3-note chime
    playTone(523, 0.15, "sfx"); // C5
    setTimeout(() => playTone(659, 0.15, "sfx"), 100); // E5
    setTimeout(() => playTone(784, 0.2, "sfx"), 200);  // G5
  },
  wrong(): void { playTone(293, 0.3, "sfx", "triangle"); },

  // Reward moments (§20.2)
  achievement(): void {
    playTone(523, 0.12, "sfx");
    setTimeout(() => playTone(659, 0.12, "sfx"), 80);
    setTimeout(() => playTone(784, 0.12, "sfx"), 160);
    setTimeout(() => playTone(1047, 0.25, "sfx"), 240);
  },
  levelUp(): void {
    playTone(392, 0.15, "sfx");
    setTimeout(() => playTone(523, 0.15, "sfx"), 120);
    setTimeout(() => playTone(659, 0.15, "sfx"), 240);
    setTimeout(() => playTone(784, 0.2, "sfx"), 360);
    setTimeout(() => playTone(1047, 0.3, "sfx"), 480);
  },
  collect(): void { playTone(1047, 0.1, "sfx"); },

  // Radar ping for notifications
  ping(): void { playTone(1500, 0.08, "sfx", "sine"); },
};
