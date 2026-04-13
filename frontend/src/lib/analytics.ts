// Privacy-first event emitter. PLAN §24.
//
// Events are buffered client-side (≤20 events or 30s) then flushed as one POST
// to /api/v1/events/. The server validates against the allow-list and strips
// anything unexpected, so this module stays intentionally dumb: no PII is ever
// added here, and we never block gameplay on the network.

import { API_BASE } from "./api";

export type EventType =
  | "session.started"
  | "session.ended"
  | "mission.started"
  | "mission.completed"
  | "mission.abandoned"
  | "quiz.answered"
  | "jigsaw.completed"
  | "collection.earned"
  | "navigation.planet_visited"
  | "dda.adjustment"
  | "streak.updated"
  | "onboarding.step_completed"
  | "break_reminder.shown"
  | "break_reminder.accepted"
  | "content.nasa_image_viewed"
  | "error.game_crash"
  | "experiment.exposed";

interface OutgoingEvent {
  event_type: EventType;
  session_id: string;
  payload: Record<string, unknown>;
}

const MAX_BUFFER = 20;
const FLUSH_MS = 30_000;
const ENDPOINT = `${API_BASE}/api/v1/events/`;

let buffer: OutgoingEvent[] = [];
let timer: ReturnType<typeof setTimeout> | null = null;
let sessionId = "";

function uuid(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  // RFC4122-ish fallback for older browsers
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

/** Start a new analytics session. Call once on app mount. Returns session id. */
export function startSession(isReturning: boolean): string {
  sessionId = uuid();
  track("session.started", {
    device_type: /Mobi|Android/i.test(navigator.userAgent) ? "mobile" : "desktop",
    screen_size: `${window.screen.width}x${window.screen.height}`,
    is_returning: isReturning,
  });
  window.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flush(true);
  });
  window.addEventListener("pagehide", () => flush(true));
  return sessionId;
}

/** Queue an event. Never throws. */
export function track(event_type: EventType, payload: Record<string, unknown> = {}): void {
  if (!sessionId) sessionId = uuid();
  buffer.push({ event_type, session_id: sessionId, payload });
  if (buffer.length >= MAX_BUFFER) {
    flush();
  } else if (!timer) {
    timer = setTimeout(() => flush(), FLUSH_MS);
  }
}

/** Send buffered events now. `useBeacon` for unload paths. */
export function flush(useBeacon = false): void {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
  if (buffer.length === 0) return;
  const body = JSON.stringify({ events: buffer });
  buffer = [];

  if (useBeacon && typeof navigator !== "undefined" && "sendBeacon" in navigator) {
    navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "application/json" }));
    return;
  }
  fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    keepalive: true,
  }).catch(() => {
    /* analytics must never surface errors to children */
  });
}
