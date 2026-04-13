import { SpaceMap } from "@/components/SpaceMap";
import { PlayerHud } from "@/components/PlayerHud";
import { Leaderboard } from "@/components/Leaderboard";
import { ConstellationView } from "@/components/Constellation";
import { AgeGroupSelector } from "@/components/AgeGroupSelector";

export default function HomePage() {
  return (
    <main className="max-w-6xl mx-auto p-4 md:p-8">
      <PlayerHud />
      <header className="mb-6">
        <h1 className="text-3xl md:text-5xl font-display">NASA Space Explorer</h1>
        <p className="text-space-lunar mt-2 text-sm md:text-base">
          Tap a planet to begin your mission. Real NASA data. Real science. Real play.
        </p>
      </header>

      <SpaceMap />

      <div className="grid gap-6 mt-8 md:grid-cols-2">
        <Leaderboard />
        <ConstellationView />
      </div>

      <div className="mt-8 glass-panel p-4">
        <AgeGroupSelector />
      </div>

      <footer className="mt-6 text-xs text-white/30">
        Real NASA data from APOD, Mars Rovers, NeoWs, EPIC, and Exoplanet Archive.
        All competition uses pseudonyms only. Weekly leaderboard resets every Monday.
      </footer>
    </main>
  );
}
