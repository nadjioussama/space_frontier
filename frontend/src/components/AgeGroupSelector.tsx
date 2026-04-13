"use client";
/**
 * Age group selector. PLAN §18.4, §22.
 * Changes UI density, font sizes, and content complexity.
 */
import clsx from "clsx";
import { motion } from "framer-motion";
import { usePlayer, type AgeGroup } from "@/store/player";
import { SoundManager } from "@/lib/sound";

const AGE_OPTIONS: { value: AgeGroup; label: string; desc: string }[] = [
  { value: "6-8", label: "6–8", desc: "Bigger text, simpler missions" },
  { value: "9-11", label: "9–11", desc: "Standard experience" },
  { value: "12-14", label: "12–14", desc: "Compact UI, harder challenges" },
];

export function AgeGroupSelector({ compact }: { compact?: boolean }) {
  const { ageGroup, setAgeGroup } = usePlayer();

  const handleSelect = (ag: AgeGroup) => {
    setAgeGroup(ag);
    SoundManager.click();
  };

  if (compact) {
    return (
      <div className="flex gap-1">
        {AGE_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => handleSelect(opt.value)}
            className={clsx(
              "px-2 py-1 rounded text-xs font-mono transition",
              ageGroup === opt.value
                ? "bg-space-accent text-space-900"
                : "bg-white/5 text-white/50 hover:bg-white/10"
            )}
          >
            {opt.label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="font-display text-xs uppercase tracking-widest text-white/50">
        Age Group
      </label>
      <div className="flex gap-2">
        {AGE_OPTIONS.map((opt) => (
          <motion.button
            key={opt.value}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleSelect(opt.value)}
            className={clsx(
              "flex-1 p-3 rounded-xl border text-center transition",
              ageGroup === opt.value
                ? "border-space-accent bg-space-accent/10 text-space-accent-light"
                : "border-white/10 bg-white/5 text-white/60 hover:border-white/20"
            )}
          >
            <div className="font-display text-lg">{opt.label}</div>
            <div className="text-xs mt-1 opacity-70">{opt.desc}</div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
