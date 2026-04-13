/**
 * Tests for lib/queries.ts — TanStack Query hooks with offline fallback.
 */
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// Mock dependencies
jest.mock("@/lib/api", () => ({
  apiFetch: jest.fn(),
}));
jest.mock("@/lib/offlineStore", () => ({
  cacheToday: jest.fn(),
  cacheMission: jest.fn(),
  readCachedToday: jest.fn(),
  readCachedMission: jest.fn(),
}));
jest.mock("@/lib/seed", () => ({
  SEED_TODAY: { apod: { title: "Seed APOD" }, mission_slug: "seed-mission" },
  SEED_MISSION: { slug: "seed-mission", title: "Seed Mission", mission_type: "apod_daily", xp_reward: 50, difficulty: 3, apod: null, jigsaw: null, quizzes: [] },
}));

import { apiFetch } from "@/lib/api";
import { readCachedToday, readCachedMission, cacheToday, cacheMission } from "@/lib/offlineStore";
import { SEED_TODAY, SEED_MISSION } from "@/lib/seed";

const mockApiFetch = apiFetch as jest.MockedFunction<typeof apiFetch>;
const mockReadCachedToday = readCachedToday as jest.MockedFunction<typeof readCachedToday>;
const mockReadCachedMission = readCachedMission as jest.MockedFunction<typeof readCachedMission>;

function createWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client }, children);
}

describe("useToday", () => {
  beforeEach(() => jest.clearAllMocks());

  it("returns API data on success", async () => {
    const { useToday } = require("@/lib/queries");
    const apiData = { apod: { title: "Live APOD" }, mission_slug: "live-1" };
    mockApiFetch.mockResolvedValueOnce(apiData);

    const { result } = renderHook(() => useToday(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(apiData);
    expect(cacheToday).toHaveBeenCalledWith(apiData);
  });

  it("falls back to IndexedDB cache on network error", async () => {
    const { useToday } = require("@/lib/queries");
    const cached = { apod: { title: "Cached" }, mission_slug: "cached-1" };
    mockApiFetch.mockRejectedValueOnce(new Error("offline"));
    mockReadCachedToday.mockResolvedValueOnce(cached);

    const { result } = renderHook(() => useToday(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(cached);
  });

  it("falls back to seed data when both network and cache fail", async () => {
    const { useToday } = require("@/lib/queries");
    mockApiFetch.mockRejectedValueOnce(new Error("offline"));
    mockReadCachedToday.mockResolvedValueOnce(null);

    const { result } = renderHook(() => useToday(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(SEED_TODAY);
  });
});

describe("usePlanets", () => {
  beforeEach(() => jest.clearAllMocks());

  it("fetches planets from API", async () => {
    const { usePlanets } = require("@/lib/queries");
    const planets = [{ slug: "earth", name: "Earth" }];
    mockApiFetch.mockResolvedValueOnce(planets);

    const { result } = renderHook(() => usePlanets(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(planets);
  });
});

describe("useMission", () => {
  beforeEach(() => jest.clearAllMocks());

  it("returns API data and caches it", async () => {
    const { useMission } = require("@/lib/queries");
    const mission = { slug: "test", title: "Test" };
    mockApiFetch.mockResolvedValueOnce(mission);

    const { result } = renderHook(() => useMission("test"), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mission);
    expect(cacheMission).toHaveBeenCalledWith("test", mission);
  });

  it("falls back to cached mission on error", async () => {
    const { useMission } = require("@/lib/queries");
    const cached = { slug: "cached", title: "Cached" };
    mockApiFetch.mockRejectedValueOnce(new Error("fail"));
    mockReadCachedMission.mockResolvedValueOnce(cached);

    const { result } = renderHook(() => useMission("cached"), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(cached);
  });

  it("returns seed mission when slug matches", async () => {
    const { useMission } = require("@/lib/queries");
    mockApiFetch.mockRejectedValueOnce(new Error("fail"));
    mockReadCachedMission.mockResolvedValueOnce(null);

    const { result } = renderHook(() => useMission(SEED_MISSION.slug), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(SEED_MISSION);
  });

  it("does not fetch when slug is null", () => {
    const { useMission } = require("@/lib/queries");
    const { result } = renderHook(() => useMission(null), { wrapper: createWrapper() });
    expect(result.current.fetchStatus).toBe("idle");
    expect(mockApiFetch).not.toHaveBeenCalled();
  });
});

describe("useWeeklyLeaderboard", () => {
  beforeEach(() => jest.clearAllMocks());

  it("fetches leaderboard data", async () => {
    const { useWeeklyLeaderboard } = require("@/lib/queries");
    const data = { period: "weekly", entries: [] };
    mockApiFetch.mockResolvedValueOnce(data);

    const { result } = renderHook(() => useWeeklyLeaderboard(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(data);
  });
});

describe("usePlanetLeaderboard", () => {
  beforeEach(() => jest.clearAllMocks());

  it("fetches planet-specific leaderboard", async () => {
    const { usePlanetLeaderboard } = require("@/lib/queries");
    const data = { period: "weekly", entries: [{ player_id: 1, score: 100 }] };
    mockApiFetch.mockResolvedValueOnce(data);

    const { result } = renderHook(() => usePlanetLeaderboard("earth"), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(data);
  });

  it("does not fetch with empty slug", () => {
    const { usePlanetLeaderboard } = require("@/lib/queries");
    const { result } = renderHook(() => usePlanetLeaderboard(""), { wrapper: createWrapper() });
    expect(result.current.fetchStatus).toBe("idle");
  });
});

describe("useConstellations", () => {
  beforeEach(() => jest.clearAllMocks());

  it("fetches constellation data", async () => {
    const { useConstellations } = require("@/lib/queries");
    const data = [{ slug: "astronomy", name: "Astronomy", stars: [] }];
    mockApiFetch.mockResolvedValueOnce(data);

    const { result } = renderHook(() => useConstellations(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(data);
  });
});

describe("useProgress", () => {
  beforeEach(() => jest.clearAllMocks());

  it("fetches player progress", async () => {
    const { useProgress } = require("@/lib/queries");
    const data = { total_xp: 500, rank: "Scout" };
    mockApiFetch.mockResolvedValueOnce(data);

    const { result } = renderHook(() => useProgress(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(data);
  });
});

describe("useDDA", () => {
  beforeEach(() => jest.clearAllMocks());

  it("fetches DDA state", async () => {
    const { useDDA } = require("@/lib/queries");
    const data = { level: 3, accuracy: 0.75 };
    mockApiFetch.mockResolvedValueOnce(data);

    const { result } = renderHook(() => useDDA(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(data);
  });
});
