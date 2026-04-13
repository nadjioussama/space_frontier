"use client";
/**
 * Knowledge Constellation — skill tree visualization. PLAN §3.4.
 *
 * Each star = a concept learned. Stars connect into constellations = topic mastery.
 * Constellations light up in the player's personal "night sky".
 * SVG-based for accessibility and reduced motion support.
 */
import { motion } from "framer-motion";
import { useState } from "react";
import { useConstellations } from "@/lib/queries";
import type { ConstellationData, ConstellationStar } from "@/lib/api";

function StarNode({ star, onClick }: { star: ConstellationStar; onClick: () => void }) {
  const earned = star.earned;
  return (
    <motion.g
      whileHover={{ scale: 1.3 }}
      whileTap={{ scale: 0.95 }}
      className="cursor-pointer"
      onClick={onClick}
    >
      <circle
        cx={star.x}
        cy={star.y}
        r={earned ? 6 : 4}
        fill={earned ? "#F0A500" : "#1B2735"}
        stroke={earned ? "#F0A500" : "#2E86AB"}
        strokeWidth={earned ? 2 : 1}
        opacity={earned ? 1 : 0.5}
      />
      {earned && (
        <circle
          cx={star.x}
          cy={star.y}
          r={10}
          fill="none"
          stroke="#F0A500"
          strokeWidth={0.5}
          opacity={0.3}
        >
          <animate
            attributeName="r"
            values="8;12;8"
            dur="3s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.3;0.1;0.3"
            dur="3s"
            repeatCount="indefinite"
          />
        </circle>
      )}
      <text
        x={star.x}
        y={star.y + 16}
        textAnchor="middle"
        fill={earned ? "#E8E8E8" : "#9BA3AF"}
        fontSize="7"
        fontFamily="Nunito, sans-serif"
      >
        {star.name}
      </text>
    </motion.g>
  );
}

function ConstellationMap({ constellation }: { constellation: ConstellationData }) {
  const [selected, setSelected] = useState<ConstellationStar | null>(null);

  // Draw connecting lines between prerequisites
  const starsBySlug = Object.fromEntries(constellation.stars.map((s) => [s.slug, s]));

  return (
    <div className="glass-panel p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-display text-space-accent-light text-sm tracking-widest uppercase">
          {constellation.name}
        </h3>
        <span className="text-xs font-mono text-space-gold">
          {constellation.earned_count}/{constellation.total_count}
        </span>
      </div>
      <svg viewBox="0 0 100 100" className="w-full aspect-square">
        {/* Prerequisite lines */}
        {constellation.stars.map((star) =>
          star.prerequisites.map((preSlug) => {
            const pre = starsBySlug[preSlug];
            if (!pre) return null;
            return (
              <line
                key={`${pre.slug}-${star.slug}`}
                x1={pre.x}
                y1={pre.y}
                x2={star.x}
                y2={star.y}
                stroke={pre.earned && star.earned ? "#F0A500" : "#2E86AB"}
                strokeWidth={0.5}
                opacity={pre.earned && star.earned ? 0.6 : 0.2}
                strokeDasharray={pre.earned && star.earned ? "none" : "2 2"}
              />
            );
          })
        )}
        {/* Star nodes */}
        {constellation.stars.map((star) => (
          <StarNode key={star.slug} star={star} onClick={() => setSelected(star)} />
        ))}
      </svg>

      {/* Selected star detail */}
      {selected && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 p-2 bg-white/5 rounded-lg text-xs"
        >
          <div className="font-display text-space-accent-light">{selected.name}</div>
          <div className="text-white/60 mt-1">{selected.description || "Complete missions to earn this star."}</div>
          <div className="flex gap-2 mt-1 text-white/40">
            <span>+{selected.xp_value} XP</span>
            {selected.earned && <span className="text-space-gold">Earned</span>}
          </div>
        </motion.div>
      )}
    </div>
  );
}

export function ConstellationView() {
  const { data, isLoading } = useConstellations();

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="skeleton h-48 rounded-xl" />
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="glass-panel p-6 text-center">
        <div className="font-display text-space-accent-light mb-2">Knowledge Constellation</div>
        <p className="text-white/50 text-sm">
          Complete missions to discover your first stars. Each concept you learn lights up your personal night sky.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="font-display text-xl tracking-widest uppercase text-space-accent-light">
        Your Night Sky
      </h2>
      <div className="grid gap-4 sm:grid-cols-2">
        {data.map((c) => (
          <ConstellationMap key={c.slug} constellation={c} />
        ))}
      </div>
    </div>
  );
}
