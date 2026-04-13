"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useWeeklyLeaderboard } from "@/lib/queries";
import type { LeaderboardEntry } from "@/lib/api";

const RANK_COLORS: Record<number, string> = {
  1: "text-space-gold",
  2: "text-space-lunar",
  3: "text-space-rust",
};

function EntryRow({ entry, index }: { entry: LeaderboardEntry; index: number }) {
  const rankColor = RANK_COLORS[entry.rank] || "text-white/70";
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03, duration: 0.2 }}
      className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 transition"
    >
      <span className={`font-mono text-sm w-8 text-right ${rankColor}`}>
        #{entry.rank}
      </span>
      <span className="flex-1 font-body truncate">{entry.display_name}</span>
      <span className="font-mono text-space-gold text-sm">{entry.score.toLocaleString()} XP</span>
    </motion.div>
  );
}

export function Leaderboard() {
  const { data, isLoading, error } = useWeeklyLeaderboard();

  return (
    <div className="glass-panel p-4">
      <h2 className="font-display text-space-accent-light text-lg mb-3 tracking-widest uppercase">
        Weekly Leaderboard
      </h2>
      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="skeleton h-8 rounded-lg" />
          ))}
        </div>
      )}
      {error && !data && (
        <div className="text-space-warn text-sm">Leaderboard unavailable right now.</div>
      )}
      {data && data.entries.length === 0 && (
        <div className="text-white/50 text-sm">No scores yet this week. Be the first!</div>
      )}
      <AnimatePresence>
        {data?.entries.map((entry, i) => (
          <EntryRow key={entry.player_id} entry={entry} index={i} />
        ))}
      </AnimatePresence>
      <div className="mt-2 text-[10px] text-white/30 uppercase tracking-widest">
        Resets every Monday &middot; Pseudonyms only
      </div>
    </div>
  );
}
