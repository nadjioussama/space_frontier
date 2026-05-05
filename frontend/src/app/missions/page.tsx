"use client";
/**
 * Cross-API missions listing page. PLAN §2.3.
 * Shows multi-source missions that combine data from different NASA APIs.
 */
import Link from "next/link";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { PlayerHud } from "@/components/PlayerHud";
import { SoundManager } from "@/lib/sound";

type PlanetMissions = {
  planet: { slug: string; name: string };
  missions: Array<{
    slug: string;
    title: string;
    mission_type: string;
    xp_reward: number;
    difficulty: number;
  }>;
};

const MISSION_TYPE_LABELS: Record<string, { label: string; color: string }> = {
  cross_api: { label: "Cross-API", color: "text-space-purple" },
  apod_daily: { label: "APOD", color: "text-space-teal" },
  mars_rover: { label: "Mars", color: "text-space-rust" },
  neo_defense: { label: "NEO", color: "text-space-warn" },
  epic_observer: { label: "EPIC", color: "text-space-accent-light" },
  exoplanet_explorer: { label: "Exoplanet", color: "text-space-purple" },
};

export default function MissionsPage() {
  // Fetch all planet detail pages to get mission lists
  const { data: earthMissions } = useQuery({
    queryKey: ["planet-detail", "earth"],
    queryFn: () => apiFetch<PlanetMissions>("/api/v1/planets/earth/"),
    staleTime: 60 * 60 * 1000,
  });

  const crossApiMissions = earthMissions?.missions.filter((m) => m.mission_type === "cross_api") ?? [];
  const allMissions = earthMissions?.missions ?? [];

  return (
    <>
      <PlayerHud />
      <div className="max-w-5xl mx-auto p-4 md:p-8 space-y-8">
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <Link href="/" className="text-sm text-space-accent/80 hover:text-space-accent-light transition">
            &larr; Space Map
          </Link>
        </motion.header>

        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl md:text-3xl font-display"
        >
          All Missions
        </motion.h1>

        {crossApiMissions.length > 0 && (
          <section>
            <h2 className="font-display text-lg text-space-purple mb-3 tracking-widest uppercase">
              Cross-API Missions
            </h2>
            <p className="text-white/50 text-sm mb-4">
              Combine data from multiple NASA sources to answer big questions.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              {crossApiMissions.map((m, i) => (
                <motion.div
                  key={m.slug}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    href={`/mission/${m.slug}`}
                    onClick={() => SoundManager.click()}
                    className="block glass-panel p-4 border-space-purple/20 hover:border-space-purple/40 transition-all hover:shadow-glow group"
                  >
                    <div className="font-display text-space-purple group-hover:text-space-purple/80 transition">
                      {m.title}
                    </div>
                    <div className="flex gap-3 mt-2 text-xs text-white/40">
                      <span>Difficulty {m.difficulty}/10</span>
                      <span className="text-space-gold">+{m.xp_reward} XP</span>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </section>
        )}

        <section>
          <h2 className="font-display text-lg text-space-accent-light mb-3 tracking-widest uppercase">
            All Available Missions
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {allMissions
              .filter((m) => m.mission_type !== "cross_api")
              .map((m, i) => {
                const typeInfo = MISSION_TYPE_LABELS[m.mission_type] || { label: m.mission_type, color: "text-white/60" };
                return (
                  <motion.div
                    key={m.slug}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <Link
                      href={`/mission/${m.slug}`}
                      onClick={() => SoundManager.click()}
                      className="block glass-panel p-3 hover:border-white/20 transition-all group"
                    >
                      <div className="font-body text-sm group-hover:text-white transition">{m.title}</div>
                      <div className="flex gap-2 mt-1 text-[10px] text-white/40">
                        <span className={typeInfo.color}>{typeInfo.label}</span>
                        <span>Lv.{m.difficulty}</span>
                        <span className="text-space-gold">+{m.xp_reward}</span>
                      </div>
                    </Link>
                  </motion.div>
                );
              })}
          </div>
        </section>
      </div>
    </>
  );
}
