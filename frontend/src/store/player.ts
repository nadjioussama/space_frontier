// Local, client-only player state. Phase 5 adds streak tracking, DDA level,
// and age-group for UI density. Persists to localStorage.
"use client";
import { create } from "zustand";

const STORAGE_KEY = "nse:player:v2";

export type AgeGroup = "6-8" | "9-11" | "12-14" | "adult";

type PlayerState = {
  anonId: string;
  totalXp: number;
  rank: string;
  completedMissionSlugs: string[];
  ageGroup: AgeGroup;
  ddaLevel: number;
  streak: number;
  soundMuted: boolean;
  addXp: (xp: number) => void;
  markCompleted: (slug: string) => void;
  setAgeGroup: (ag: AgeGroup) => void;
  setDDALevel: (level: number) => void;
  incrementStreak: () => void;
  toggleSound: () => void;
  _rehydrate: () => void;
};

function rankFor(xp: number): string {
  if (xp >= 5000) return "Legend";
  if (xp >= 2000) return "Admiral";
  if (xp >= 800) return "Captain";
  if (xp >= 300) return "Commander";
  if (xp >= 100) return "Pilot";
  return "Cadet";
}

function newAnonId(): string {
  return "anon-" + Math.random().toString(36).slice(2, 10);
}

export const usePlayer = create<PlayerState>((set, get) => ({
  anonId: "",
  totalXp: 0,
  rank: "Cadet",
  completedMissionSlugs: [],
  ageGroup: "9-11",
  ddaLevel: 3,
  streak: 0,
  soundMuted: false,

  addXp: (xp) => {
    const totalXp = get().totalXp + xp;
    const next = { totalXp, rank: rankFor(totalXp) };
    set(next);
    persist({ ...get(), ...next });
  },

  markCompleted: (slug) => {
    if (get().completedMissionSlugs.includes(slug)) return;
    const completedMissionSlugs = [...get().completedMissionSlugs, slug];
    set({ completedMissionSlugs });
    persist({ ...get(), completedMissionSlugs });
  },

  setAgeGroup: (ag) => {
    set({ ageGroup: ag });
    // Apply to <html> for CSS age-adaptive styles
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-age", ag);
    }
    persist({ ...get(), ageGroup: ag });
  },

  setDDALevel: (level) => {
    set({ ddaLevel: level });
    persist({ ...get(), ddaLevel: level });
  },

  incrementStreak: () => {
    const streak = get().streak + 1;
    set({ streak });
    persist({ ...get(), streak });
  },

  toggleSound: () => {
    const soundMuted = !get().soundMuted;
    set({ soundMuted });
    persist({ ...get(), soundMuted });
  },

  _rehydrate: () => {
    if (typeof window === "undefined") return;
    // Migrate from v1 if needed
    const v1 = window.localStorage.getItem("nse:player:v1");
    const raw = window.localStorage.getItem(STORAGE_KEY) || v1;
    try {
      if (raw) {
        const data = JSON.parse(raw);
        const state = {
          anonId: data.anonId || newAnonId(),
          totalXp: data.totalXp || 0,
          rank: data.rank || "Cadet",
          completedMissionSlugs: data.completedMissionSlugs || [],
          ageGroup: (data.ageGroup as AgeGroup) || "9-11",
          ddaLevel: data.ddaLevel || 3,
          streak: data.streak || 0,
          soundMuted: data.soundMuted || false,
        };
        set(state);
        // Apply age group to document
        document.documentElement.setAttribute("data-age", state.ageGroup);
        if (!data.anonId) persist({ ...get(), anonId: get().anonId });
        // Clean up v1
        if (v1) window.localStorage.removeItem("nse:player:v1");
        return;
      }
    } catch { /* fall through */ }
    const anonId = newAnonId();
    set({ anonId });
    document.documentElement.setAttribute("data-age", "9-11");
    persist({ ...get(), anonId });
  },
}));

function persist(snapshot: Partial<PlayerState>) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        anonId: snapshot.anonId,
        totalXp: snapshot.totalXp,
        rank: snapshot.rank,
        completedMissionSlugs: snapshot.completedMissionSlugs,
        ageGroup: snapshot.ageGroup,
        ddaLevel: snapshot.ddaLevel,
        streak: snapshot.streak,
        soundMuted: snapshot.soundMuted,
      })
    );
  } catch { /* quota / private-mode */ }
}
