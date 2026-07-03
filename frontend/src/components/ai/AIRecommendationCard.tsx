import type { AIRecommendationResponse } from "@/types";

interface AIRecommendationCardProps {
  recommendation: AIRecommendationResponse;
}

export function AIRecommendationCard({ recommendation: r }: AIRecommendationCardProps) {
  const confidenceColor =
    r.confidence >= 80
      ? "text-success border-success/20 bg-success/10"
      : r.confidence >= 50
        ? "text-yellow-400 border-yellow-400/20 bg-yellow-400/10"
        : "text-danger border-danger/20 bg-danger/10";

  const riskColor =
    r.risk_level.toLowerCase() === "low"
      ? "bg-success/10 text-success border-success/20"
      : r.risk_level.toLowerCase() === "medium"
        ? "bg-yellow-400/10 text-yellow-400 border-yellow-400/20"
        : "bg-danger/10 text-danger border-danger/20";

  return (
    <section className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-text">AI Recommendation</h3>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${confidenceColor}`}
        >
          <span className="h-1.5 w-1.5 rounded-full bg-current" />
          {r.confidence}% confidence
        </span>
      </div>

      {/* Summary */}
      <p className="mb-6 rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3 text-sm font-medium italic leading-relaxed text-text/90 [overflow-wrap:anywhere] break-words">
        {r.summary}
      </p>

      {/* Mix Direction */}
      <div className="mb-6">
        <Field label="Mix Direction" value={r.mix_direction} />
      </div>

      {/* Transition */}
      <div className="mb-6">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
          Transition
        </h4>
        <div className="grid gap-3 md:grid-cols-2">
          <Stat label="Quality" value={r.transition_quality} />
          <Stat label="Type" value={r.transition_type} />
        </div>
      </div>

      {/* Tempo Analysis */}
      <div className="mb-6">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
          Tempo Analysis
        </h4>
        <div className="grid gap-3 md:grid-cols-2">
          <Stat label="Difference" value={r.tempo_analysis.difference} />
          <Stat label="Recommendation" value={r.tempo_analysis.recommendation} />
        </div>
      </div>

      {/* Energy Analysis */}
      <div className="mb-6">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
          Energy Analysis
        </h4>
        <div className="grid gap-3 md:grid-cols-2">
          <Stat label="Difference" value={r.energy_analysis.difference} />
          <Stat label="Recommendation" value={r.energy_analysis.recommendation} />
        </div>
      </div>

      {/* Compatibility Analysis */}
      <div className="mb-6">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
          Compatibility Analysis
        </h4>
        <div className="grid gap-3 md:grid-cols-2">
          <Stat label="Score" value={r.compatibility_analysis.score} />
          <Stat label="Interpretation" value={r.compatibility_analysis.interpretation} />
        </div>
      </div>

      {/* Mix Strategy */}
      <div className="mb-6">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
          Mix Strategy
        </h4>
        <div className="grid gap-3 md:grid-cols-3">
          <Stat label="Before" value={r.mix_strategy.before_transition} />
          <Stat label="During" value={r.mix_strategy.during_transition} />
          <Stat label="After" value={r.mix_strategy.after_transition} />
        </div>
      </div>

      {/* DJ Execution */}
      <div className="mb-6">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
          DJ Execution
        </h4>
        <div className="grid gap-3 md:grid-cols-2">
          <Stat label="Loop" value={r.dj_execution.loop} />
          <Stat label="EQ" value={r.dj_execution.eq} />
          <Stat label="Filter" value={r.dj_execution.filter} />
          <Stat label="Tempo Fader" value={r.dj_execution.tempo_fader} />
          <Stat label="Phrase Matching" value={r.dj_execution.phrase_matching} />
          <Stat label="Cue Point" value={r.dj_execution.cue_point} />
        </div>
      </div>

      {/* Professional Notes */}
      {r.professional_notes && (
        <div className="mb-6">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
            Professional Notes
          </h4>
          <p className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3 text-sm leading-relaxed text-text-secondary [overflow-wrap:anywhere] break-words">
            {r.professional_notes}
          </p>
        </div>
      )}

      {/* Club Tip */}
      {r.club_tip && (
        <div className="mb-6">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
            Club Tip
          </h4>
          <p className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3 text-sm leading-relaxed text-text-secondary [overflow-wrap:anywhere] break-words">
            {r.club_tip}
          </p>
        </div>
      )}

      {/* Risks */}
      {r.risks.length > 0 && (
        <div className="mb-6">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
            Risks
          </h4>
          <div className="flex flex-wrap gap-2">
            {r.risks.map((risk, i) => (
              <span
                key={i}
                className="rounded-full border border-danger/20 bg-danger/10 px-3 py-1 text-xs font-medium text-danger [overflow-wrap:anywhere] break-words"
              >
                {risk}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Best Use Case + Risk Level */}
      <div className="grid gap-3 md:grid-cols-2">
        {r.best_use_case && (
          <div>
            <p className="mb-1 text-xs uppercase tracking-[0.15em] text-text-secondary">
              Best Use Case
            </p>
            <p className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3 text-sm font-medium leading-relaxed text-text [overflow-wrap:anywhere] break-words">
              {r.best_use_case}
            </p>
          </div>
        )}
        <div>
          <p className="mb-1 text-xs uppercase tracking-[0.15em] text-text-secondary">
            Risk Level
          </p>
          <span
            className={`inline-block rounded-full border px-4 py-2 text-sm font-semibold ${riskColor}`}
          >
            {r.risk_level}
          </span>
        </div>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.15em] text-text-secondary">{label}</p>
      <p className="mt-1 text-base font-semibold text-text [overflow-wrap:anywhere] break-words">
        {value}
      </p>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.15em] text-text-secondary">{label}</p>
      <p className="mt-1 text-sm leading-relaxed text-text [overflow-wrap:anywhere] break-words">
        {value}
      </p>
    </div>
  );
}
