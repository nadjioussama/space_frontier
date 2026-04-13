// IndexedDB-backed offline cache. PLAN §6.2 L1.
// Stores (1) player progress and (2) last-fetched mission payloads so the game
// keeps working when the backend is unreachable.
import { get, set, del, keys } from "idb-keyval";

const MISSION_PREFIX = "mission:";
const TODAY_KEY = "nasa:today";

export async function cacheMission(slug: string, data: unknown): Promise<void> {
  await set(`${MISSION_PREFIX}${slug}`, { data, cachedAt: Date.now() });
}

export async function readCachedMission<T>(slug: string): Promise<T | null> {
  const entry = await get<{ data: T; cachedAt: number }>(`${MISSION_PREFIX}${slug}`);
  return entry?.data ?? null;
}

export async function cacheToday(data: unknown): Promise<void> {
  await set(TODAY_KEY, { data, cachedAt: Date.now() });
}

export async function readCachedToday<T>(): Promise<T | null> {
  const entry = await get<{ data: T; cachedAt: number }>(TODAY_KEY);
  return entry?.data ?? null;
}

export async function listCachedMissionSlugs(): Promise<string[]> {
  const ks = await keys();
  return ks
    .map(String)
    .filter((k) => k.startsWith(MISSION_PREFIX))
    .map((k) => k.slice(MISSION_PREFIX.length));
}

export async function clearAll(): Promise<void> {
  const ks = await keys();
  await Promise.all(ks.map((k) => del(k)));
}
