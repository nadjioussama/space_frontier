"use client";
import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { usePlayer } from "@/store/player";
import { SoundToggle } from "./SoundToggle";
import { SoundManager } from "@/lib/sound";

export function PlayerHud() {
  const { rank, totalXp, streak, ddaLevel, _rehydrate } = usePlayer();

  useEffect(() => {
    _rehydrate();
    SoundManager.init();
  }, [_rehydrate]);

  return (
    <div className="fixed top-3 right-3 z-40 flex items-start gap-2">
      <SoundToggle />
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="glass-panel px-3 py-2 text-xs"
      >
        <div className="font-display text-space-accent-light">{rank}</div>
        <div className="font-mono text-space-gold">
          <AnimatePresence mode="popLayout">
            <motion.span
              key={totalXp}
              initial={{ scale: 1.3, color: "#F0A500" }}
              animate={{ scale: 1, color: "#F0A500" }}
              transition={{ duration: 0.3 }}
            >
              {totalXp.toLocaleString()}
            </motion.span>
          </AnimatePresence>
          {" "}XP
        </div>
        <div className="flex gap-2 mt-1 text-[10px] text-white/40">
          {streak > 0 && <span title="Daily streak">🔥 {streak}d</span>}
          <span title="Difficulty level">Lv.{ddaLevel}</span>
        </div>
      </motion.div>
    </div>
  );
}
