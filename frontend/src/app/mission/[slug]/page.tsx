"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { MissionViewport } from "@/components/MissionViewport";
import { PlayerHud } from "@/components/PlayerHud";
import { useMission } from "@/lib/queries";

export default function MissionPage() {
  const params = useParams<{ slug: string }>();
  const slug = Array.isArray(params.slug) ? params.slug[0] : params.slug;
  const { data, error, isLoading } = useMission(slug ?? null);

  return (
    <>
      <PlayerHud />
      {isLoading && (
        <div className="max-w-5xl mx-auto p-8 text-white/70">Loading mission...</div>
      )}
      {error && !data && (
        <div className="max-w-5xl mx-auto p-8 space-y-3">
          <div className="text-space-warn">
            We couldn&apos;t load this mission and don&apos;t have a saved copy.
          </div>
          <Link href="/" className="text-space-accent text-sm">
            &larr; Back to Space Map
          </Link>
        </div>
      )}
      {data && <MissionViewport mission={data} />}
    </>
  );
}
