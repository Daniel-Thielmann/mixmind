import type { CompatibilityResult } from "@/types";

interface CompatibilityCardProps {
  compatibility: CompatibilityResult;
}

export function CompatibilityCard({ compatibility }: CompatibilityCardProps) {
  return (
    <section className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7">
      <h3 className="mb-5 text-lg font-semibold text-text">Compatibility</h3>

      <div className="grid gap-3 md:grid-cols-2">
        <Stat label="Score" value={`${compatibility.compatibility_score.toFixed(1)}%`} />
        <Stat label="Tempo Match" value={compatibility.tempo_match} />
        <Stat label="Energy Match" value={compatibility.energy_match} />
        <Stat label="Overall Rating" value={compatibility.overall_rating} />
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.15em] text-text-secondary">{label}</p>
      <p className="mt-1 text-base font-semibold text-text">{value}</p>
    </div>
  );
}
