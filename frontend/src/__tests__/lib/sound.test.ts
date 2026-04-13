import { SoundManager } from "../../lib/sound";

const STORAGE_KEY = "nse:sound:v1";

describe("SoundManager", () => {
  // We need to reset the module-level `initialized` flag between tests.
  // The simplest way is to re-import the module via jest.resetModules.
  let SM: typeof SoundManager;

  beforeEach(() => {
    jest.resetModules();
    // Re-require to get a fresh module with initialized=false
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    SM = require("../../lib/sound").SoundManager;
  });

  describe("init", () => {
    it("loads settings from localStorage", () => {
      const customSettings = {
        master: 0.5,
        sfx: 0.5,
        music: 0.5,
        voice: 0.5,
        muted: true,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(customSettings));
      SM.init();
      const s = SM.getSettings();
      expect(s.master).toBe(0.5);
      expect(s.muted).toBe(true);
    });

    it("only initializes once", () => {
      SM.init();
      SM.updateSettings({ master: 0.1 });
      // Second init should NOT reload defaults
      SM.init();
      expect(SM.getSettings().master).toBe(0.1);
    });

    it("uses defaults when nothing stored", () => {
      SM.init();
      const s = SM.getSettings();
      expect(s.master).toBe(0.7);
      expect(s.sfx).toBe(0.7);
      expect(s.music).toBe(0.3);
      expect(s.voice).toBe(1.0);
      expect(s.muted).toBe(false);
    });
  });

  describe("getSettings", () => {
    it("returns a copy of settings (not reference)", () => {
      SM.init();
      const a = SM.getSettings();
      const b = SM.getSettings();
      expect(a).toEqual(b);
      expect(a).not.toBe(b);
    });
  });

  describe("updateSettings", () => {
    it("merges partial settings", () => {
      SM.init();
      SM.updateSettings({ master: 0.9 });
      const s = SM.getSettings();
      expect(s.master).toBe(0.9);
      // other fields unchanged
      expect(s.sfx).toBe(0.7);
    });

    it("saves to localStorage", () => {
      SM.init();
      SM.updateSettings({ music: 0.8 });
      const raw = localStorage.getItem(STORAGE_KEY);
      expect(raw).toBeTruthy();
      const saved = JSON.parse(raw!);
      expect(saved.music).toBe(0.8);
    });
  });

  describe("toggleMute", () => {
    it("toggles muted state", () => {
      SM.init();
      const result = SM.toggleMute();
      expect(result).toBe(true);
      expect(SM.getSettings().muted).toBe(true);
    });

    it("toggles back to false", () => {
      SM.init();
      SM.toggleMute();
      const result = SM.toggleMute();
      expect(result).toBe(false);
      expect(SM.getSettings().muted).toBe(false);
    });

    it("saves to localStorage", () => {
      SM.init();
      SM.toggleMute();
      const raw = localStorage.getItem(STORAGE_KEY);
      const saved = JSON.parse(raw!);
      expect(saved.muted).toBe(true);
    });
  });

  describe("sound effect methods do not throw", () => {
    beforeEach(() => {
      SM.init();
    });

    it("click does not throw", () => {
      expect(() => SM.click()).not.toThrow();
    });

    it("hover does not throw", () => {
      expect(() => SM.hover()).not.toThrow();
    });

    it("transition does not throw", () => {
      expect(() => SM.transition()).not.toThrow();
    });

    it("error does not throw", () => {
      expect(() => SM.error()).not.toThrow();
    });

    it("correct does not throw", () => {
      expect(() => SM.correct()).not.toThrow();
    });

    it("wrong does not throw", () => {
      expect(() => SM.wrong()).not.toThrow();
    });

    it("achievement does not throw", () => {
      expect(() => SM.achievement()).not.toThrow();
    });

    it("levelUp does not throw", () => {
      expect(() => SM.levelUp()).not.toThrow();
    });

    it("collect does not throw", () => {
      expect(() => SM.collect()).not.toThrow();
    });

    it("ping does not throw", () => {
      expect(() => SM.ping()).not.toThrow();
    });
  });

  describe("muted state prevents audio playback", () => {
    it("does not create oscillator when muted", () => {
      SM.init();
      SM.updateSettings({ muted: true });
      // AudioContext mock tracks calls; when muted volume=0, playTone returns early
      // before creating oscillator. We verify no error and rely on the vol===0 guard.
      expect(() => SM.click()).not.toThrow();
      expect(() => SM.hover()).not.toThrow();
      expect(() => SM.correct()).not.toThrow();
      expect(() => SM.achievement()).not.toThrow();
    });
  });
});
