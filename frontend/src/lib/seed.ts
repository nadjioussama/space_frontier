// Ultimate fallback — a curated APOD bundled with the app so the game can
// always start even on a totally fresh install with the backend down.
// PLAN §6.7: "Everything down -> seed bundle".
import type { MissionDetail, TodayPayload } from "./api";

export const SEED_TODAY: TodayPayload = {
  apod: {
    date: "2024-07-12",
    title: "A Welcome From the Universe",
    explanation:
      "While we reach NASA for today's real image, here is a classic view of the cosmos — a reminder that space is both vast and beautiful. Every star you see is a sun, and many have planets of their own.",
    media_type: "image",
    image: "/seed/starfield.svg",
    copyright: "",
  },
  mission_slug: "apod-seed",
};

export const SEED_MISSION: MissionDetail = {
  slug: "apod-seed",
  title: "Mission: A Welcome From the Universe",
  mission_type: "apod_daily",
  xp_reward: 30,
  difficulty: 1,
  apod: SEED_TODAY.apod,
  jigsaw: {
    image_url: "/seed/starfield.svg",
    piece_count: 12,
    grid_cols: 4,
    grid_rows: 3,
    piece_data: Array.from({ length: 12 }, (_, i) => {
      const cols = 4, rows = 3;
      const row = Math.floor(i / cols), col = i % cols;
      return { id: i, row, col, u: col / cols, v: row / rows, w: 1 / cols, h: 1 / rows };
    }),
  },
  quizzes: [
    {
      id: -1,
      question: "How many stars, roughly, live in our Milky Way galaxy?",
      options: ["A few hundred", "A few thousand", "About 100 billion", "About 100"],
      difficulty: 2,
    },
    {
      id: -2,
      question: "True or false: every star in the sky is actually a distant sun.",
      options: ["True", "False", "Only the bright ones", "Only the red ones"],
      difficulty: 1,
    },
  ],
};
