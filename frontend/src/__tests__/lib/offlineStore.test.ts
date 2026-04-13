import {
  cacheMission,
  readCachedMission,
  cacheToday,
  readCachedToday,
  listCachedMissionSlugs,
  clearAll,
} from "../../lib/offlineStore";

// The idb-keyval mock is set up in setupTests.ts with an in-memory Map.
// Access the backing store to verify / reset between tests.
const idb = require("idb-keyval") as {
  get: jest.Mock;
  set: jest.Mock;
  del: jest.Mock;
  keys: jest.Mock;
  __store: Map<string, unknown>;
};

beforeEach(() => {
  idb.__store.clear();
  jest.clearAllMocks();
});

describe("offlineStore", () => {
  describe("cacheMission + readCachedMission", () => {
    it("round-trips mission data", async () => {
      const missionData = { slug: "mars-1", title: "Mars Mission", xp_reward: 50 };
      await cacheMission("mars-1", missionData);
      const result = await readCachedMission("mars-1");
      expect(result).toEqual(missionData);
    });

    it("returns null for unknown slug", async () => {
      const result = await readCachedMission("nonexistent");
      expect(result).toBeNull();
    });
  });

  describe("cacheToday + readCachedToday", () => {
    it("round-trips today data", async () => {
      const todayData = { apod: { date: "2024-07-12", title: "Stars" }, mission_slug: "m1" };
      await cacheToday(todayData);
      const result = await readCachedToday();
      expect(result).toEqual(todayData);
    });

    it("returns null when nothing cached", async () => {
      const result = await readCachedToday();
      expect(result).toBeNull();
    });
  });

  describe("listCachedMissionSlugs", () => {
    it("returns only mission keys (strips prefix)", async () => {
      await cacheMission("alpha", { title: "Alpha" });
      await cacheMission("beta", { title: "Beta" });
      // Also cache a today entry which should NOT appear
      await cacheToday({ apod: {} });

      const slugs = await listCachedMissionSlugs();
      expect(slugs).toContain("alpha");
      expect(slugs).toContain("beta");
      expect(slugs).toHaveLength(2);
    });

    it("returns empty array when no missions cached", async () => {
      // Only non-mission data
      await cacheToday({ apod: {} });
      const slugs = await listCachedMissionSlugs();
      expect(slugs).toEqual([]);
    });
  });

  describe("clearAll", () => {
    it("empties the store", async () => {
      await cacheMission("m1", {});
      await cacheMission("m2", {});
      await cacheToday({});
      expect(idb.__store.size).toBeGreaterThan(0);

      await clearAll();
      expect(idb.__store.size).toBe(0);
    });
  });
});
