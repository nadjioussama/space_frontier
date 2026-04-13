// Thin fetch wrapper. Raises on non-2xx so TanStack Query can retry/propagate.
// The env var is inlined at build time by Next.js.
export const API_BASE =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_BASE) ||
  "http://localhost:8000";

/** Resolve a backend-relative path ("/media/apod/xxx.jpg") into an absolute
 * URL against the Django origin. Absolute URLs and frontend-local paths
 * ("/seed/...") are returned untouched so the seed bundle keeps working. */
export function resolveAsset(url: string | null | undefined): string {
  if (!url) return "";
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith("/seed/") || url.startsWith("/_next/")) return url;
  if (url.startsWith("/")) return `${API_BASE}${url}`;
  return url;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || res.statusText);
  }
  return (await res.json()) as T;
}

// Types mirror the DRF serializers in backend/apps/games/serializers.py
export type Apod = {
  date: string;
  title: string;
  explanation: string;
  media_type: "image" | "video" | string;
  image: string;
  copyright?: string;
};

export type TodayPayload = { apod: Apod; mission_slug: string | null; neo_approaching_count?: number };

export type Planet = {
  slug: string;
  name: string;
  description: string;
  is_unlocked: boolean;
  mission_count: number;
};

export type Quiz = {
  id: number;
  question: string;
  options: string[];
  difficulty: number;
};

export type Jigsaw = {
  image_url: string;
  piece_count: number;
  grid_cols: number;
  grid_rows: number;
  piece_data: Array<{
    id: number; row: number; col: number;
    u: number; v: number; w: number; h: number;
  }>;
};

export type MissionDetail = {
  slug: string;
  title: string;
  mission_type: string;
  xp_reward: number;
  difficulty: number;
  apod: Apod | null;
  jigsaw: Jigsaw | null;
  quizzes: Quiz[];
  is_cross_api?: boolean;
  cross_api_sources?: string[];
};

export type AttemptPayload = {
  quiz_answers: Array<{ quiz_id: number; answer: string }>;
  jigsaw_completed: boolean;
};

export type DDAInfo = {
  level: number;
  accuracy: number;
};

export type AttemptResult = {
  mission_slug: string;
  results: Array<{
    quiz_id: number;
    correct: boolean;
    correct_answer?: string;
    explanation?: string;
  }>;
  xp_earned: number;
  progress: { attempt_id: number; total_xp: number; rank: string; dda: DDAInfo };
};

// Phase 5: Leaderboard
export type LeaderboardEntry = {
  player_id: number;
  display_name: string;
  score: number;
  rank: number;
};

export type LeaderboardResponse = {
  period: string;
  entries: LeaderboardEntry[];
};

// Phase 5: Constellation (skill tree)
export type ConstellationStar = {
  id: number;
  slug: string;
  name: string;
  description: string;
  xp_value: number;
  x: number;
  y: number;
  earned: boolean;
  prerequisites: string[];
};

export type ConstellationData = {
  slug: string;
  name: string;
  topic: string;
  description: string;
  icon: string;
  stars: ConstellationStar[];
  earned_count: number;
  total_count: number;
};

// Phase 5: Player progress
export type PlayerProgress = {
  total_xp: number;
  rank: string;
  attempt_count: number;
  missions_completed: number;
  dda_level: number;
  dda_accuracy: number;
  leaderboard_rank: number | null;
  leaderboard_score: number;
  streak: number;
  longest_streak: number;
  earned_stars: number;
  achievements: number;
};

// Phase 5: DDA state
export type DDAState = {
  level: number;
  accuracy: number;
  topic_levels: Record<string, number>;
  config: {
    quiz: {
      choices: number;
      hint_tiers: number;
      auto_nudge_seconds: number | null;
      time_limit: number | null;
      question_difficulty_max: number;
    };
    jigsaw: {
      piece_count: number;
      rotation_enabled: boolean;
      preview_enabled: boolean;
      edge_hints: boolean;
    };
  };
};
