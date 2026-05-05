import { usePlayer } from "../../store/player";

const STORAGE_KEY = "nse:player:v2";
const V1_KEY = "nse:player:v1";

const initialState = {
  anonId: "",
  totalXp: 0,
  rank: "Cadet",
  completedMissionSlugs: [] as string[],
  ageGroup: "9-11" as const,
  ddaLevel: 3,
  streak: 0,
  soundMuted: false,
};

function resetStore() {
  usePlayer.setState({ ...initialState });
}

describe("player store", () => {
  beforeEach(() => {
    resetStore();
  });

  // --- Initial state ---
  describe("initial state", () => {
    it("has empty anonId", () => {
      expect(usePlayer.getState().anonId).toBe("");
    });

    it("has totalXp 0", () => {
      expect(usePlayer.getState().totalXp).toBe(0);
    });

    it("has rank Cadet", () => {
      expect(usePlayer.getState().rank).toBe("Cadet");
    });

    it("has empty completedMissionSlugs", () => {
      expect(usePlayer.getState().completedMissionSlugs).toEqual([]);
    });

    it("has default ageGroup 9-11", () => {
      expect(usePlayer.getState().ageGroup).toBe("9-11");
    });

    it("has default ddaLevel 3", () => {
      expect(usePlayer.getState().ddaLevel).toBe(3);
    });

    it("has streak 0", () => {
      expect(usePlayer.getState().streak).toBe(0);
    });

    it("has soundMuted false", () => {
      expect(usePlayer.getState().soundMuted).toBe(false);
    });
  });

  // --- addXp ---
  describe("addXp", () => {
    it("increments totalXp", () => {
      usePlayer.getState().addXp(50);
      expect(usePlayer.getState().totalXp).toBe(50);
    });

    it("accumulates XP across multiple calls", () => {
      usePlayer.getState().addXp(50);
      usePlayer.getState().addXp(60);
      expect(usePlayer.getState().totalXp).toBe(110);
    });

    it("updates rank correctly when crossing threshold", () => {
      usePlayer.getState().addXp(100);
      expect(usePlayer.getState().rank).toBe("Pilot");
    });

    it("persists to localStorage", () => {
      usePlayer.getState().addXp(50);
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
      expect(saved.totalXp).toBe(50);
    });
  });

  // --- rankFor thresholds ---
  describe("rank thresholds via addXp", () => {
    it("Cadet for 0-99 XP", () => {
      usePlayer.getState().addXp(0);
      expect(usePlayer.getState().rank).toBe("Cadet");
      resetStore();
      usePlayer.getState().addXp(99);
      expect(usePlayer.getState().rank).toBe("Cadet");
    });

    it("Pilot for 100-299 XP", () => {
      usePlayer.getState().addXp(100);
      expect(usePlayer.getState().rank).toBe("Pilot");
      resetStore();
      usePlayer.getState().addXp(299);
      expect(usePlayer.getState().rank).toBe("Pilot");
    });

    it("Commander for 300-799 XP", () => {
      usePlayer.getState().addXp(300);
      expect(usePlayer.getState().rank).toBe("Commander");
      resetStore();
      usePlayer.getState().addXp(799);
      expect(usePlayer.getState().rank).toBe("Commander");
    });

    it("Captain for 800-1999 XP", () => {
      usePlayer.getState().addXp(800);
      expect(usePlayer.getState().rank).toBe("Captain");
      resetStore();
      usePlayer.getState().addXp(1999);
      expect(usePlayer.getState().rank).toBe("Captain");
    });

    it("Admiral for 2000-4999 XP", () => {
      usePlayer.getState().addXp(2000);
      expect(usePlayer.getState().rank).toBe("Admiral");
      resetStore();
      usePlayer.getState().addXp(4999);
      expect(usePlayer.getState().rank).toBe("Admiral");
    });

    it("Legend for 5000+ XP", () => {
      usePlayer.getState().addXp(5000);
      expect(usePlayer.getState().rank).toBe("Legend");
      resetStore();
      usePlayer.getState().addXp(10000);
      expect(usePlayer.getState().rank).toBe("Legend");
    });
  });

  // --- markCompleted ---
  describe("markCompleted", () => {
    it("adds slug to completedMissionSlugs", () => {
      usePlayer.getState().markCompleted("mission-a");
      expect(usePlayer.getState().completedMissionSlugs).toContain("mission-a");
    });

    it("prevents duplicate slugs", () => {
      usePlayer.getState().markCompleted("mission-a");
      usePlayer.getState().markCompleted("mission-a");
      expect(usePlayer.getState().completedMissionSlugs).toEqual(["mission-a"]);
    });

    it("persists to localStorage", () => {
      usePlayer.getState().markCompleted("mission-b");
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
      expect(saved.completedMissionSlugs).toContain("mission-b");
    });
  });

  // --- setAgeGroup ---
  describe("setAgeGroup", () => {
    it("updates ageGroup", () => {
      usePlayer.getState().setAgeGroup("6-8");
      expect(usePlayer.getState().ageGroup).toBe("6-8");
    });

    it("sets document data-age attribute", () => {
      usePlayer.getState().setAgeGroup("12-14");
      expect(document.documentElement.getAttribute("data-age")).toBe("12-14");
    });

    it("persists to localStorage", () => {
      usePlayer.getState().setAgeGroup("adult");
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
      expect(saved.ageGroup).toBe("adult");
    });
  });

  // --- setDDALevel ---
  describe("setDDALevel", () => {
    it("updates ddaLevel", () => {
      usePlayer.getState().setDDALevel(5);
      expect(usePlayer.getState().ddaLevel).toBe(5);
    });

    it("persists to localStorage", () => {
      usePlayer.getState().setDDALevel(7);
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
      expect(saved.ddaLevel).toBe(7);
    });
  });

  // --- incrementStreak ---
  describe("incrementStreak", () => {
    it("increments streak by 1", () => {
      usePlayer.getState().incrementStreak();
      expect(usePlayer.getState().streak).toBe(1);
    });

    it("increments multiple times", () => {
      usePlayer.getState().incrementStreak();
      usePlayer.getState().incrementStreak();
      usePlayer.getState().incrementStreak();
      expect(usePlayer.getState().streak).toBe(3);
    });

    it("persists to localStorage", () => {
      usePlayer.getState().incrementStreak();
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
      expect(saved.streak).toBe(1);
    });
  });

  // --- toggleSound ---
  describe("toggleSound", () => {
    it("toggles soundMuted from false to true", () => {
      usePlayer.getState().toggleSound();
      expect(usePlayer.getState().soundMuted).toBe(true);
    });

    it("toggles back to false", () => {
      usePlayer.getState().toggleSound();
      usePlayer.getState().toggleSound();
      expect(usePlayer.getState().soundMuted).toBe(false);
    });

    it("persists to localStorage", () => {
      usePlayer.getState().toggleSound();
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
      expect(saved.soundMuted).toBe(true);
    });
  });

  // --- _rehydrate ---
  describe("_rehydrate", () => {
    it("loads saved state from localStorage", () => {
      const saved = {
        anonId: "anon-existing",
        totalXp: 250,
        rank: "Pilot",
        completedMissionSlugs: ["m1"],
        ageGroup: "12-14",
        ddaLevel: 5,
        streak: 3,
        soundMuted: true,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
      usePlayer.getState()._rehydrate();
      const state = usePlayer.getState();
      expect(state.anonId).toBe("anon-existing");
      expect(state.totalXp).toBe(250);
      expect(state.rank).toBe("Pilot");
      expect(state.completedMissionSlugs).toEqual(["m1"]);
      expect(state.ageGroup).toBe("12-14");
      expect(state.ddaLevel).toBe(5);
      expect(state.streak).toBe(3);
      expect(state.soundMuted).toBe(true);
    });

    it("generates anonId if missing in saved state", () => {
      const saved = { totalXp: 100, rank: "Pilot" };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
      usePlayer.getState()._rehydrate();
      const state = usePlayer.getState();
      expect(state.anonId).toBeTruthy();
      expect(state.anonId).not.toBe("");
    });

    it("generates anonId when no saved state exists", () => {
      usePlayer.getState()._rehydrate();
      expect(usePlayer.getState().anonId).toBeTruthy();
      expect(usePlayer.getState().anonId).not.toBe("");
    });

    it("migrates from v1 storage key", () => {
      const v1Data = {
        anonId: "anon-v1",
        totalXp: 50,
        rank: "Cadet",
        completedMissionSlugs: [],
        ageGroup: "9-11",
        ddaLevel: 3,
        streak: 1,
        soundMuted: false,
      };
      localStorage.setItem(V1_KEY, JSON.stringify(v1Data));
      usePlayer.getState()._rehydrate();
      expect(usePlayer.getState().anonId).toBe("anon-v1");
      expect(usePlayer.getState().totalXp).toBe(50);
      expect(usePlayer.getState().streak).toBe(1);
      // v1 key should be removed after migration
      expect(localStorage.getItem(V1_KEY)).toBeNull();
    });

    it("sets data-age attribute on document", () => {
      const saved = { anonId: "anon-x", ageGroup: "6-8" };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
      usePlayer.getState()._rehydrate();
      expect(document.documentElement.getAttribute("data-age")).toBe("6-8");
    });
  });

  // --- persist ---
  describe("persist", () => {
    it("saves to localStorage with correct shape", () => {
      usePlayer.getState().addXp(200);
      usePlayer.getState().markCompleted("slug-1");
      usePlayer.getState().setAgeGroup("adult");
      usePlayer.getState().setDDALevel(4);
      usePlayer.getState().incrementStreak();
      usePlayer.getState().toggleSound();

      const raw = localStorage.getItem(STORAGE_KEY);
      expect(raw).toBeTruthy();
      const saved = JSON.parse(raw!);
      expect(saved).toEqual(
        expect.objectContaining({
          totalXp: 200,
          rank: "Pilot",
          completedMissionSlugs: ["slug-1"],
          ageGroup: "adult",
          ddaLevel: 4,
          streak: 1,
          soundMuted: true,
        })
      );
    });
  });
});
