"use client";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { useMemo, useState } from "react";
import Link from "next/link";
import type { MissionDetail, AttemptResult } from "@/lib/api";
import { apiFetch } from "@/lib/api";
import { QuizPanel } from "./Quiz";
import { usePlayer } from "@/store/player";
import { SoundManager } from "@/lib/sound";

const JigsawCanvas = dynamic(() => import("./Jigsaw"), { ssr: false });

type Props = { mission: MissionDetail };

type SubmitState =
  | { phase: "playing" }
  | { phase: "submitting" }
  | { phase: "done"; xp: number; correct: number; total: number; offline?: boolean; ddaLevel?: number }
  | { phase: "error"; message: string };

export function MissionViewport({ mission }: Props) {
  const [jigsawDone, setJigsawDone] = useState(mission.jigsaw == null);
  const [state, setState] = useState<SubmitState>({ phase: "playing" });
  const addXp = usePlayer((s) => s.addXp);
  const markCompleted = usePlayer((s) => s.markCompleted);
  const setDDALevel = usePlayer((s) => s.setDDALevel);
  const incrementStreak = usePlayer((s) => s.incrementStreak);

  const needsJigsaw = useMemo(() => mission.jigsaw != null, [mission.jigsaw]);

  async function handleSubmit(answers: Array<{ quiz_id: number; answer: string }>) {
    setState({ phase: "submitting" });
    try {
      const res = await apiFetch<AttemptResult>(
        `/api/v1/missions/${mission.slug}/attempt/`,
        {
          method: "POST",
          body: JSON.stringify({ quiz_answers: answers, jigsaw_completed: jigsawDone }),
        }
      );
      const correct = res.results.filter((r) => r.correct).length;
      addXp(res.xp_earned);
      markCompleted(mission.slug);
      incrementStreak();

      // Update DDA level from server response
      if (res.progress?.dda) {
        setDDALevel(res.progress.dda.level);
      }

      // Play appropriate sound
      if (correct === res.results.length) {
        SoundManager.achievement();
      } else if (correct > 0) {
        SoundManager.correct();
      } else {
        SoundManager.wrong();
      }

      setState({
        phase: "done",
        xp: res.xp_earned,
        correct,
        total: res.results.length,
        ddaLevel: res.progress?.dda?.level,
      });
    } catch (err) {
      const xp = Math.round(mission.xp_reward * 0.5);
      addXp(xp);
      markCompleted(mission.slug);
      SoundManager.collect();
      setState({
        phase: "done",
        xp,
        correct: answers.length,
        total: answers.length,
        offline: true,
      });
    }
  }

  const handleJigsawComplete = () => {
    setJigsawDone(true);
    SoundManager.collect();
  };

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-8 space-y-6">
      <motion.header
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-between"
      >
        <Link href="/" className="text-sm text-space-accent/80 hover:text-space-accent-light transition">
          &larr; Space Map
        </Link>
        <div className="flex items-center gap-3 text-xs uppercase tracking-widest text-white/50">
          {mission.is_cross_api && (
            <span className="text-space-purple bg-space-purple/10 border border-space-purple/30 px-2 py-0.5 rounded">
              Cross-API
            </span>
          )}
          <span>Difficulty {mission.difficulty}/10</span>
          <span className="text-space-gold">+{mission.xp_reward} XP</span>
        </div>
      </motion.header>

      <motion.h1
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="text-2xl md:text-3xl font-display"
      >
        {mission.title}
      </motion.h1>

      {mission.apod && (
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="glass-panel p-4 text-sm leading-relaxed"
        >
          <div className="font-display text-space-accent-light mb-1">
            NASA Picture of the Day — {mission.apod.date}
          </div>
          <p className="text-white/80">{mission.apod.explanation}</p>
          {mission.apod.copyright && (
            <p className="text-white/40 text-xs mt-2">Image: {mission.apod.copyright}</p>
          )}
        </motion.section>
      )}

      {needsJigsaw && mission.jigsaw && (
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-display mb-3">Jigsaw</h2>
          <JigsawCanvas jigsaw={mission.jigsaw} onComplete={handleJigsawComplete} />
        </motion.section>
      )}

      <motion.section
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
      >
        <h2 className="text-xl font-display mb-3">Quiz</h2>
        <QuizPanel
          quizzes={mission.quizzes}
          onComplete={handleSubmit}
          disabled={state.phase !== "playing"}
        />
      </motion.section>

      <AnimatePresence>
        {state.phase === "done" && (
          <motion.section
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="bg-space-ok/10 border border-space-ok/40 rounded-xl p-5 shadow-glow-ok"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 400, delay: 0.1 }}
              className="font-display text-space-ok text-xl"
            >
              Mission complete! +{state.xp} XP
            </motion.div>
            <div className="text-sm text-white/80 mt-2">
              You got {state.correct} of {state.total} quiz answers
              {state.total > 0 ? ` (${Math.round((state.correct / state.total) * 100)}%)` : ""}.
            </div>
            {state.ddaLevel && (
              <div className="text-xs text-white/40 mt-1">
                Difficulty adjusted to level {state.ddaLevel}
              </div>
            )}
            {state.offline && (
              <div className="text-xs text-space-warn mt-2">
                Submitted offline — XP saved locally; the server will re-grade when you reconnect.
              </div>
            )}
            <Link href="/" className="inline-block mt-4 btn-primary text-sm">
              Return to Space Map &rarr;
            </Link>
          </motion.section>
        )}
      </AnimatePresence>
    </div>
  );
}
