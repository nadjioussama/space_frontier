// Analytics tests need fresh module state for each test
let trackFn: typeof import("../../lib/analytics").track;
let flushFn: typeof import("../../lib/analytics").flush;
let startSessionFn: typeof import("../../lib/analytics").startSession;

const originalFetch = globalThis.fetch;

beforeEach(() => {
  jest.resetModules();
  globalThis.fetch = jest.fn().mockResolvedValue({ ok: true });
  Object.defineProperty(navigator, "sendBeacon", {
    value: jest.fn().mockReturnValue(true),
    writable: true,
    configurable: true,
  });
  // Re-require fresh module
  const analytics = require("../../lib/analytics");
  trackFn = analytics.track;
  flushFn = analytics.flush;
  startSessionFn = analytics.startSession;
});

afterEach(() => {
  globalThis.fetch = originalFetch;
});

describe("analytics", () => {
  describe("track", () => {
    it("buffers events without immediately sending", () => {
      trackFn("mission.started", { slug: "m1" });
      expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it("auto-flushes at MAX_BUFFER (20 events)", () => {
      for (let i = 0; i < 20; i++) {
        trackFn("quiz.answered", { i });
      }
      expect(globalThis.fetch).toHaveBeenCalledTimes(1);
      const callArgs = (globalThis.fetch as jest.Mock).mock.calls[0];
      expect(callArgs[0]).toContain("/api/v1/events/");
      const body = JSON.parse(callArgs[1].body);
      expect(body.events).toHaveLength(20);
    });

    it("never throws on network error", () => {
      (globalThis.fetch as jest.Mock).mockRejectedValue(new Error("Network down"));
      expect(() => {
        for (let i = 0; i < 20; i++) {
          trackFn("quiz.answered", { i });
        }
      }).not.toThrow();
    });
  });

  describe("flush", () => {
    it("sends POST to /api/v1/events/", () => {
      trackFn("mission.started", {});
      flushFn();
      expect(globalThis.fetch).toHaveBeenCalledTimes(1);
      const callArgs = (globalThis.fetch as jest.Mock).mock.calls[0];
      expect(callArgs[0]).toContain("/api/v1/events/");
      expect(callArgs[1].method).toBe("POST");
      expect(callArgs[1].headers["Content-Type"]).toBe("application/json");
    });

    it("clears buffer after flush", () => {
      trackFn("mission.started", {});
      flushFn();
      // Second flush should be noop
      flushFn();
      expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    });

    it("is a noop when buffer is empty", () => {
      flushFn();
      expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it("uses sendBeacon when useBeacon is true", () => {
      trackFn("session.ended", {});
      flushFn(true);
      expect(navigator.sendBeacon).toHaveBeenCalledTimes(1);
      expect(globalThis.fetch).not.toHaveBeenCalled();
      const beaconArgs = (navigator.sendBeacon as jest.Mock).mock.calls[0];
      expect(beaconArgs[0]).toContain("/api/v1/events/");
    });
  });

  describe("startSession", () => {
    it("returns a session ID", () => {
      const sid = startSessionFn(false);
      expect(typeof sid).toBe("string");
      expect(sid.length).toBeGreaterThan(0);
    });

    it("tracks session.started event", () => {
      startSessionFn(true);
      flushFn();
      expect(globalThis.fetch).toHaveBeenCalledTimes(1);
      const body = JSON.parse(
        (globalThis.fetch as jest.Mock).mock.calls[0][1].body
      );
      expect(body.events[0].event_type).toBe("session.started");
      expect(body.events[0].payload.is_returning).toBe(true);
    });

    it("includes device_type and screen_size in session.started payload", () => {
      startSessionFn(false);
      flushFn();
      const body = JSON.parse(
        (globalThis.fetch as jest.Mock).mock.calls[0][1].body
      );
      const payload = body.events[0].payload;
      expect(payload).toHaveProperty("device_type");
      expect(payload).toHaveProperty("screen_size");
    });
  });
});
