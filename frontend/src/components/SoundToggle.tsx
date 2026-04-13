"use client";
import { useEffect } from "react";
import { usePlayer } from "@/store/player";
import { SoundManager } from "@/lib/sound";

export function SoundToggle() {
  const { soundMuted, toggleSound } = usePlayer();

  useEffect(() => {
    SoundManager.init();
    if (soundMuted) SoundManager.updateSettings({ muted: true });
  }, [soundMuted]);

  const handleToggle = () => {
    toggleSound();
    SoundManager.toggleMute();
    if (!soundMuted) SoundManager.click();
  };

  return (
    <button
      onClick={handleToggle}
      className="btn-space text-xs bg-white/5 border border-white/10"
      aria-label={soundMuted ? "Unmute sounds" : "Mute sounds"}
      title={soundMuted ? "Unmute" : "Mute"}
    >
      {soundMuted ? "🔇" : "🔊"}
    </button>
  );
}
