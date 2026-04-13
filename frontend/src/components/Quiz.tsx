"use client";
import clsx from "clsx";
import { motion } from "framer-motion";
import { useState } from "react";
import type { Quiz } from "@/lib/api";
import { SoundManager } from "@/lib/sound";

type Props = {
  quizzes: Quiz[];
  onComplete: (answers: Array<{ quiz_id: number; answer: string }>) => void;
  disabled?: boolean;
};

export function QuizPanel({ quizzes, onComplete, disabled }: Props) {
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const allAnswered = quizzes.every((q) => answers[q.id] != null);

  const handlePick = (qid: number, opt: string) => {
    setAnswers((s) => ({ ...s, [qid]: opt }));
    SoundManager.click();
  };

  const handleSubmit = () => {
    SoundManager.transition();
    onComplete(quizzes.map((q) => ({ quiz_id: q.id, answer: answers[q.id] })));
  };

  return (
    <div className="space-y-6">
      {quizzes.map((q, idx) => (
        <motion.div
          key={q.id}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.08, duration: 0.25 }}
          className="glass-panel p-4"
        >
          <div className="text-xs uppercase tracking-widest text-space-accent/80 mb-2">
            Question {idx + 1}
          </div>
          <div className="font-body text-lg mb-3">{q.question}</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {q.options.map((opt) => {
              const picked = answers[q.id] === opt;
              return (
                <motion.button
                  key={opt}
                  type="button"
                  disabled={disabled}
                  whileHover={{ scale: disabled ? 1 : 1.02 }}
                  whileTap={{ scale: disabled ? 1 : 0.97 }}
                  onClick={() => handlePick(q.id, opt)}
                  className={clsx(
                    "text-left px-3 py-2 rounded-lg border transition-colors",
                    picked
                      ? "border-space-accent bg-space-accent/10 text-space-accent-light shadow-glow"
                      : "border-white/10 bg-black/20 hover:border-white/30"
                  )}
                >
                  {opt}
                </motion.button>
              );
            })}
          </div>
        </motion.div>
      ))}
      <motion.button
        type="button"
        disabled={!allAnswered || disabled}
        whileHover={allAnswered && !disabled ? { scale: 1.02, boxShadow: "0 0 20px rgba(46,134,171,0.4)" } : undefined}
        whileTap={allAnswered && !disabled ? { scale: 0.97 } : undefined}
        onClick={handleSubmit}
        className={clsx(
          "w-full py-3 rounded-xl font-display tracking-widest uppercase transition",
          allAnswered && !disabled
            ? "bg-space-accent text-space-900 hover:brightness-110"
            : "bg-white/10 text-white/40 cursor-not-allowed"
        )}
      >
        {disabled ? "Submitted" : "Submit Answers"}
      </motion.button>
    </div>
  );
}
