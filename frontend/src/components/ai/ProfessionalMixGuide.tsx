"use client";

import { useState, memo } from "react";
import type { AIRecommendationResponse, CompatibilityResult } from "@/types";

interface ProfessionalMixGuideProps {
  recommendation: AIRecommendationResponse;
  compatibility: CompatibilityResult;
}

// -----------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------

function difficultyBadge(difficulty: string) {
  const map: Record<string, { label: string; cls: string }> = {
    "Very Easy": { label: "Easy Mix", cls: "border-success/30 bg-success/10 text-success" },
    Easy: { label: "Easy Mix", cls: "border-success/20 bg-success/5 text-success/80" },
    Medium: { label: "Moderate Mix", cls: "border-yellow-400/30 bg-yellow-400/10 text-yellow-400" },
    Hard: { label: "Hard Mix", cls: "border-orange-400/30 bg-orange-400/10 text-orange-400" },
    Expert: { label: "Expert Mix", cls: "border-danger/30 bg-danger/10 text-danger" },
  };
  return map[difficulty] ?? map.Medium;
}

function matchBadge(overallRating: string) {
  const map: Record<string, { label: string; cls: string }> = {
    Excellent: { label: "Excellent", cls: "text-success" },
    "Very Good": { label: "Very Good", cls: "text-success/80" },
    Good: { label: "Good", cls: "text-yellow-400" },
    Fair: { label: "Fair", cls: "text-orange-400" },
    Poor: { label: "Risky", cls: "text-danger" },
  };
  return map[overallRating] ?? { label: "AI Assisted", cls: "text-text-secondary" };
}

function riskColor(level: string) {
  switch (level.toLowerCase()) {
    case "low": return "text-success";
    case "medium": return "text-yellow-400";
    case "high": return "text-danger";
    default: return "text-text-secondary";
  }
}

function scoreColor(score: number) {
  if (score >= 80) return "#21d969";
  if (score >= 60) return "#facc15";
  if (score >= 40) return "#fb923c";
  return "#ff5b6e";
}

// -----------------------------------------------------------------------
// Score Ring (72px, compact)
// -----------------------------------------------------------------------

function ScoreRing({ score }: { score: number }) {
  const size = 72;
  const stroke = 6;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = scoreColor(score);

  return (
    <div className="relative inline-flex items-center justify-center shrink-0">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={stroke}
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <span className="absolute text-base font-bold tracking-tight" style={{ color }}>
        {score}
      </span>
    </div>
  );
}

// -----------------------------------------------------------------------
// Main component
// -----------------------------------------------------------------------

export function ProfessionalMixGuide({ recommendation: r, compatibility }: ProfessionalMixGuideProps) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const diff = difficultyBadge(r.mix_difficulty);
  const match = matchBadge(compatibility.overall_rating);

  const timelineEntries = r.transition_timeline
    ? Object.entries(r.transition_timeline)
    : [];

  const djExecEntries = Object.entries(r.dj_execution) as [string, string][];

  return (
    <section className="rounded-xl border border-zinc-800 bg-card/75 p-4 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-5">

      {/* ── HEADER ── */}
      <header className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-text">Professional Mix Guide</h3>
          <span className="rounded-full border border-primary/20 bg-primary/5 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-primary">
            AI Assisted
          </span>
        </div>
        <span className={`rounded-full border px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider ${diff.cls}`}>
          {diff.label}
        </span>
      </header>

      {/* ── SCORE + QUICK STATS ── */}
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <ScoreRing score={r.dj_score} />

        <div className="flex flex-1 flex-wrap items-center gap-x-4 gap-y-1 min-w-[180px]">
          <MiniStat label="Risk" value={r.risk_level} valueClass={riskColor(r.risk_level)} />
          <MiniStat label="Transition" value={r.recommended_transition_length} />
          <MiniStat label="Quality" value={r.transition_quality} valueClass={
            r.transition_quality.toLowerCase() === "high" ? "text-success"
            : r.transition_quality.toLowerCase() === "medium" ? "text-yellow-400"
            : "text-danger"
          } />
          <MiniStat label="Type" value={r.transition_type} />
        </div>
      </div>

      {/* ── CONFIDENCE BAR ── */}
      <ConfidenceBar confidence={r.confidence} />

      {/* ── SUMMARY ── */}
      {r.summary && (
        <div className="my-4 rounded-lg border border-primary/10 bg-primary/[0.02] px-4 py-3 text-center">
          <p className="text-sm md:text-base font-medium leading-relaxed text-text/90 line-clamp-3">
            &ldquo;{r.summary}&rdquo;
          </p>
        </div>
      )}

      {/* ── BEST USE CASE ── */}
      {r.best_use_case && (
        <div className="mb-3 text-center">
          <span className="inline-flex items-center gap-1 rounded-full border border-primary/20 bg-primary/5 px-2 py-0.5 text-[9px] font-medium text-primary">
            Best for {r.best_use_case}
          </span>
        </div>
      )}

      {/* ── EXECUTION ── */}
      <div className="mb-3">
        <h4 className="mb-1.5 text-[9px] font-semibold uppercase tracking-[0.15em] text-text-secondary/60">Execution</h4>
        <div className="grid gap-2 sm:grid-cols-3">
          <ExecutionCard label="Before" value={r.mix_strategy.before_transition} />
          <ExecutionCard label="During" value={r.mix_strategy.during_transition} />
          <ExecutionCard label="After" value={r.mix_strategy.after_transition} />
        </div>
      </div>

      {/* ── ADVANCED DETAILS (single accordion) ── */}
      <AdvancedAccordion open={advancedOpen} onToggle={() => setAdvancedOpen((v) => !v)}>
        {/* Tempo */}
        <Section title="Tempo Analysis">
          <CompactRow label="Difference" value={r.tempo_analysis.difference} />
          <CompactRow label="Recommendation" value={r.tempo_analysis.recommendation} />
        </Section>

        <Divider />

        {/* Energy */}
        <Section title="Energy Analysis">
          <CompactRow label="Difference" value={r.energy_analysis.difference} />
          <CompactRow label="Recommendation" value={r.energy_analysis.recommendation} />
        </Section>

        <Divider />

        {/* Compatibility */}
        <Section title="Compatibility">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5 text-xs">
            <span className="text-text-secondary/50">Score:</span>
            <span className="font-semibold text-text">{compatibility.compatibility_score.toFixed(1)}%</span>
            <span className={`text-[10px] font-medium ${match.cls}`}>({match.label})</span>
            <span className="text-text-secondary/30">|</span>
            <span className="text-text-secondary/50">LLM:</span>
            <span className="text-text/80">{r.compatibility_analysis.score}</span>
          </div>
          {r.compatibility_analysis.interpretation && (
            <p className="mt-1 text-xs leading-relaxed text-text-secondary line-clamp-2">
              {r.compatibility_analysis.interpretation}
            </p>
          )}
        </Section>

        <Divider />

        {/* DJ Execution */}
        {djExecEntries.length > 0 && (
          <>
            <Section title="DJ Execution">
              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                {djExecEntries.map(([key, value]) => (
                  <div key={key} className="flex gap-1.5 text-xs">
                    <span className="shrink-0 text-text-secondary/40 capitalize">{key.replace(/_/g, " ")}:</span>
                    <span className="text-text/80 truncate">{value}</span>
                  </div>
                ))}
              </div>
            </Section>
            <Divider />
          </>
        )}

        {/* Why This Strategy */}
        {r.why_this_strategy && (
          <>
            <Section title="Why This Strategy">
              <p className="text-xs leading-relaxed text-primary/90">{r.why_this_strategy}</p>
            </Section>
            <Divider />
          </>
        )}

        {/* Alternative Strategy */}
        {r.alternative_strategy && (
          <>
            <Section title="Alternative Strategy">
              <p className="text-xs leading-relaxed text-text/80">{r.alternative_strategy}</p>
            </Section>
            <Divider />
          </>
        )}

        {/* Club Tip */}
        {r.club_tip && (
          <>
            <Section title="Club Tip">
              <div className="flex items-start gap-1.5 rounded-lg border border-success/15 bg-success/[0.03] px-2.5 py-1.5">
                <span className="mt-0.5 shrink-0 text-xs">💡</span>
                <p className="text-xs leading-relaxed text-success/80">{r.club_tip}</p>
              </div>
            </Section>
            <Divider />
          </>
        )}

        {/* Professional Notes */}
        {r.professional_notes && (
          <>
            <Section title="Professional Notes">
              <p className="text-xs leading-relaxed text-text-secondary line-clamp-4">
                {r.professional_notes}
              </p>
            </Section>
            <Divider />
          </>
        )}

        {/* Risks */}
        {r.risks.length > 0 && (
          <>
            <Section title={`Risks (${r.risks.length})`}>
              <div className="flex flex-wrap gap-1.5">
                {r.risks.slice(0, 2).map((risk, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-full border border-danger/15 bg-danger/[0.04] px-2 py-0.5 text-[10px] text-danger/80"
                  >
                    {risk}
                  </span>
                ))}
                {r.risks.length > 2 && (
                  <span className="text-[10px] text-text-secondary/40">+{r.risks.length - 2} more</span>
                )}
              </div>
            </Section>
            <Divider />
          </>
        )}

        {/* Timeline */}
        {timelineEntries.length > 0 && (
          <Section title="Transition Timeline">
            <TimelineStepper entries={timelineEntries} />
          </Section>
        )}
      </AdvancedAccordion>

      {/* ── FOOTER ── */}
      <ModelFooter
        model={r.ai_model}
        latency={r.ai_latency}
        retryCount={r.ai_retry_count}
        fallbackOccurred={r.ai_fallback_occurred}
        provider={r.ai_provider}
      />
    </section>
  );
}

// -----------------------------------------------------------------------
// Sub-components
// -----------------------------------------------------------------------

function MiniStat({ label, value, valueClass }: { label: string; value: string; valueClass?: string }) {
  return (
    <div className="leading-tight">
      <p className="text-[9px] uppercase tracking-[0.13em] text-text-secondary/50">{label}</p>
      <p className={`text-xs font-semibold ${valueClass ?? "text-text"}`}>{value}</p>
    </div>
  );
}

function ConfidenceBar({ confidence }: { confidence: number }) {
  const color = confidence >= 80 ? "#21d969" : confidence >= 50 ? "#facc15" : "#ff5b6e";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 rounded-full bg-zinc-800">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${confidence}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[9px] font-semibold text-text-secondary/60">{confidence}%</span>
    </div>
  );
}

const ExecutionCard = memo(function ExecutionCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/30 px-2.5 py-2">
      <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-text-secondary/60">{label}</p>
      <p className="mt-0.5 text-xs leading-relaxed text-text/80">{value}</p>
    </div>
  );
});

function CompactRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline gap-2 text-xs">
      <span className="shrink-0 text-text-secondary/40">{label}</span>
      <span className="text-text/80">{value}</span>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h5 className="text-[9px] font-semibold uppercase tracking-[0.15em] text-text-secondary/40 mb-1.5">{title}</h5>
      {children}
    </div>
  );
}

function Divider() {
  return <div className="my-2 border-t border-zinc-800/50" />;
}

function AdvancedAccordion({
  open,
  onToggle,
  children,
}: {
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-zinc-800 overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between bg-zinc-900/40 px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-[0.15em] text-text-secondary transition-colors hover:bg-zinc-900/70"
      >
        Advanced Details
        <svg
          className={`h-3 w-3 shrink-0 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div
        className={`transition-all duration-200 ${open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}
        style={{ display: "grid" }}
      >
        <div className="overflow-hidden">
          <div className="px-3 pb-3 pt-2">{children}</div>
        </div>
      </div>
    </div>
  );
}

function TimelineStepper({ entries }: { entries: [string, string][] }) {
  return (
    <div className="space-y-0" style={{ maxHeight: 200, overflowY: "auto" }}>
      {entries.map(([key, action], i) => (
        <div key={key} className="relative flex gap-3 pb-3 last:pb-0">
          {i < entries.length - 1 && (
            <div className="absolute left-[11px] top-4 bottom-0 w-px bg-zinc-700" />
          )}
          <div className="relative z-10 mt-1 h-[10px] w-[10px] shrink-0 rounded-full border-2 border-primary bg-zinc-900" />
          <div className="min-w-0 flex-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-primary">
              {key.replace(/_/g, " ")}
            </span>
            <p className="text-xs leading-relaxed text-text/70">{action}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function ModelFooter({
  model,
  latency,
  retryCount,
  fallbackOccurred,
  provider,
}: {
  model?: string;
  latency?: number;
  retryCount?: number;
  fallbackOccurred?: boolean;
  provider?: string;
}) {
  const info: string[] = [];
  if (model) info.push(`Generated by ${model.split("/").pop()}`);
  if (latency != null) info.push(`${latency.toFixed(1)}s`);
  if (retryCount != null) info.push(`Retry: ${retryCount}`);
  if (fallbackOccurred != null) info.push(fallbackOccurred ? "Fallback: Yes" : "Fallback: No");
  if (provider) info.push(provider);

  if (info.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap items-center justify-end gap-x-2 gap-y-0.5 border-t border-zinc-800/40 pt-2.5 text-[9px] text-text-secondary/30">
      {info.map((part, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <span className="text-text-secondary/10">|</span>}
          {part}
        </span>
      ))}
    </div>
  );
}
