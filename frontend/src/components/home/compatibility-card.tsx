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
        {/* Novo bloco de Compatibilidade Harmônica em destaque */}
        <Stat 
          label="Harmonic Match" 
          value={compatibility.harmonic_match || "N/A"} 
          highlight 
        />
        <Stat label="Tempo Match" value={compatibility.tempo_match} />
        <Stat label="Energy Match" value={compatibility.energy_match} />
        {/* Overall Rating agora ocupa duas colunas para fechar o grid perfeitamente */}
        <Stat 
          label="Overall Rating" 
          value={compatibility.overall_rating} 
          className="md:col-span-2" 
        />
      </div>
    </section>
  );
}

function Stat({ 
  label, 
  value, 
  highlight = false,
  className = ""
}: { 
  label: string; 
  value: string;
  highlight?: boolean;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border px-4 py-3 ${
      highlight 
        ? 'border-cyan-800/50 bg-cyan-950/20' 
        : 'border-zinc-800 bg-zinc-900/65'
    } ${className}`}>
      <p className="text-xs uppercase tracking-[0.15em] text-text-secondary">{label}</p>
      <p className={`mt-1 text-base font-semibold ${
        highlight 
          ? 'text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.4)]' 
          : 'text-text'
      }`}>
        {value}
      </p>
    </div>
  );
}