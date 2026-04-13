"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { useMemo } from "react";
import { usePlanets, useToday } from "@/lib/queries";
import { SoundManager } from "@/lib/sound";

type Node = { slug: string; label: string; x: number; y: number; locked?: boolean; accent?: string };

// Phase 5: all content planets are now available
const FALLBACK_NODES: Node[] = [
  { slug: "earth", label: "Earth", x: 30, y: 50, accent: "text-space-teal" },
  { slug: "mars", label: "Mars", x: 55, y: 35, accent: "text-space-rust" },
  { slug: "asteroid-belt", label: "Asteroids", x: 75, y: 55, accent: "text-space-warn" },
  { slug: "exoplanets", label: "Exoplanets", x: 50, y: 75, accent: "text-space-purple" },
];

// Planet-specific accent colors (§16)
const PLANET_ACCENTS: Record<string, string> = {
  earth: "#1ABC9C",
  mars: "#C1440E",
  "asteroid-belt": "#F0A500",
  exoplanets: "#7B2D8E",
};

export function SpaceMap() {
  const planets = usePlanets();
  const today = useToday();

  const nodes: Node[] = useMemo(() => {
    if (!planets.data || planets.data.length === 0) return FALLBACK_NODES;
    // Layout planets in a constellation-like pattern
    const positions = [
      { x: 30, y: 50 },
      { x: 55, y: 35 },
      { x: 75, y: 55 },
      { x: 50, y: 75 },
      { x: 20, y: 30 },
      { x: 80, y: 30 },
    ];
    return planets.data.map((p, i) => ({
      slug: p.slug,
      label: p.name,
      x: positions[i % positions.length].x,
      y: positions[i % positions.length].y,
      locked: !p.is_unlocked,
    }));
  }, [planets.data]);

  const earthMissionSlug = today.data?.mission_slug ?? "apod-seed";

  return (
    <div className="relative w-full h-[70vh] min-h-[420px] rounded-2xl border border-white/10 bg-gradient-to-br from-space-900 to-space-800 overflow-hidden">
      {/* Parallax star field (§18.1) */}
      <div aria-hidden className="absolute inset-0 opacity-50"
        style={{ background: "radial-gradient(1.5px 1.5px at 10% 20%, #fff 50%, transparent), radial-gradient(1px 1px at 30% 60%, #fff 50%, transparent), radial-gradient(2px 2px at 50% 15%, #E8E8E8 50%, transparent), radial-gradient(1px 1px at 70% 80%, #fff 50%, transparent), radial-gradient(1.5px 1.5px at 90% 40%, #fff 50%, transparent), radial-gradient(1px 1px at 15% 85%, #fff 50%, transparent), radial-gradient(1px 1px at 85% 10%, #9BA3AF 50%, transparent)" }}
      />
      {/* Nebula gradient overlay */}
      <div aria-hidden className="absolute inset-0 opacity-30"
        style={{ background: "radial-gradient(600px 400px at 20% 80%, rgba(123,45,142,0.15), transparent), radial-gradient(500px 300px at 80% 20%, rgba(46,134,171,0.12), transparent)" }}
      />

      {/* Orbit path lines connecting planets */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" aria-hidden>
        {nodes.length > 1 && nodes.map((n, i) => {
          if (i === 0) return null;
          const prev = nodes[i - 1];
          return (
            <line
              key={`line-${i}`}
              x1={`${prev.x}%`} y1={`${prev.y}%`}
              x2={`${n.x}%`} y2={`${n.y}%`}
              stroke="rgba(46,134,171,0.15)"
              strokeWidth="1"
              strokeDasharray="6 4"
            />
          );
        })}
      </svg>

      {nodes.map((n, i) => {
        const planetColor = PLANET_ACCENTS[n.slug] || "#2E86AB";
        const href = n.locked ? undefined : `/mission/${n.slug === "earth" ? earthMissionSlug : `${n.slug}`}`;

        if (!href || n.locked) {
          return (
            <motion.div
              key={n.slug}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1, type: "spring", stiffness: 200 }}
              className="absolute -translate-x-1/2 -translate-y-1/2 text-center"
              style={{ left: `${n.x}%`, top: `${n.y}%` }}
            >
              <div className="block w-20 h-20 rounded-full border border-white/15 bg-white/5 text-white/30 flex items-center justify-center font-display text-xs cursor-not-allowed">
                {n.label}
              </div>
              <div className="mt-1 text-[10px] uppercase tracking-widest text-white/25">locked</div>
            </motion.div>
          );
        }
        return (
          <motion.div
            key={n.slug}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1, type: "spring", stiffness: 200 }}
            className="absolute -translate-x-1/2 -translate-y-1/2 text-center"
            style={{ left: `${n.x}%`, top: `${n.y}%` }}
          >
            <Link
              href={href}
              onClick={() => SoundManager.transition()}
              className="group"
            >
              <motion.div
                whileHover={{ scale: 1.12 }}
                whileTap={{ scale: 0.95 }}
                className="block w-20 h-20 rounded-full border-2 flex items-center justify-center font-display text-xs transition-shadow"
                style={{
                  borderColor: `${planetColor}88`,
                  backgroundColor: `${planetColor}15`,
                  color: planetColor,
                  boxShadow: `0 0 12px ${planetColor}30`,
                }}
              >
                {n.label}
              </motion.div>
              <div
                className="mt-1 text-[10px] uppercase tracking-widest opacity-80"
                style={{ color: planetColor }}
              >
                play
              </div>
            </Link>
          </motion.div>
        );
      })}

      {/* Cross-API mission portal */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="absolute bottom-4 right-4"
      >
        <Link
          href="/missions"
          onClick={() => SoundManager.click()}
          className="glass-panel px-3 py-2 text-xs text-space-purple hover:text-space-purple border-space-purple/30 hover:border-space-purple/50 transition inline-block"
        >
          Cross-API Missions &rarr;
        </Link>
      </motion.div>

      <div className="absolute bottom-3 left-3 text-[10px] text-white/30 uppercase tracking-widest">
        {today.data?.neo_approaching_count
          ? `${today.data.neo_approaching_count} NEOs approaching today`
          : "Explore the cosmos"}
      </div>
    </div>
  );
}
