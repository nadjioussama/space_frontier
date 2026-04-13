// TanStack Query hooks with layered offline fallback:
//   network -> IndexedDB -> bundled seed
// This is the frontend half of PLAN §6.7's resilience story.
"use client";
import { useQuery } from "@tanstack/react-query";
import {
  apiFetch,
  ConstellationData,
  DDAState,
  LeaderboardResponse,
  MissionDetail,
  Planet,
  PlayerProgress,
  TodayPayload,
} from "./api";
import {
  cacheMission,
  cacheToday,
  readCachedMission,
  readCachedToday,
} from "./offlineStore";
import { SEED_MISSION, SEED_TODAY } from "./seed";

export function useToday() {
  return useQuery<TodayPayload>({
    queryKey: ["today"],
    queryFn: async () => {
      try {
        const data = await apiFetch<TodayPayload>("/api/v1/nasa/today/");
        await cacheToday(data);
        return data;
      } catch (err) {
        const cached = await readCachedToday<TodayPayload>();
        if (cached) return cached;
        return SEED_TODAY;
      }
    },
    staleTime: 60 * 60 * 1000,       // 1h
  });
}

export function usePlanets() {
  return useQuery<Planet[]>({
    queryKey: ["planets"],
    queryFn: () => apiFetch<Planet[]>("/api/v1/planets/"),
    staleTime: 6 * 60 * 60 * 1000,   // 6h
  });
}

export function useMission(slug: string | null) {
  return useQuery<MissionDetail>({
    queryKey: ["mission", slug],
    enabled: !!slug,
    queryFn: async () => {
      if (!slug) throw new Error("no slug");
      try {
        const data = await apiFetch<MissionDetail>(`/api/v1/missions/${slug}/`);
        await cacheMission(slug, data);
        return data;
      } catch (err) {
        const cached = await readCachedMission<MissionDetail>(slug);
        if (cached) return cached;
        if (slug === SEED_MISSION.slug) return SEED_MISSION;
        throw err;
      }
    },
    staleTime: 24 * 60 * 60 * 1000,  // 24h
  });
}

// --- Phase 5: Leaderboard ---

export function useWeeklyLeaderboard() {
  return useQuery<LeaderboardResponse>({
    queryKey: ["leaderboard", "weekly"],
    queryFn: () => apiFetch<LeaderboardResponse>("/api/v1/leaderboard/weekly/"),
    staleTime: 5 * 60 * 1000,        // 5 min
  });
}

export function usePlanetLeaderboard(slug: string) {
  return useQuery<LeaderboardResponse>({
    queryKey: ["leaderboard", "planet", slug],
    queryFn: () => apiFetch<LeaderboardResponse>(`/api/v1/leaderboard/planet/${slug}/`),
    staleTime: 5 * 60 * 1000,
    enabled: !!slug,
  });
}

// --- Phase 5: Constellations ---

export function useConstellations() {
  return useQuery<ConstellationData[]>({
    queryKey: ["constellations"],
    queryFn: () => apiFetch<ConstellationData[]>("/api/v1/progress/constellations/"),
    staleTime: 10 * 60 * 1000,       // 10 min
  });
}

// --- Phase 5: Progress ---

export function useProgress() {
  return useQuery<PlayerProgress>({
    queryKey: ["progress"],
    queryFn: () => apiFetch<PlayerProgress>("/api/v1/progress/me/"),
    staleTime: 60 * 1000,            // 1 min
  });
}

// --- Phase 5: DDA ---

export function useDDA() {
  return useQuery<DDAState>({
    queryKey: ["dda"],
    queryFn: () => apiFetch<DDAState>("/api/v1/progress/dda/"),
    staleTime: 30 * 1000,
  });
}
