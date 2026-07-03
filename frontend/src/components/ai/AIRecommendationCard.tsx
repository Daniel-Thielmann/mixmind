"use client";

import { useState } from "react";
import type { AIRecommendationResponse } from "@/types";

interface AIRecommendationCardProps {
  recommendation: AIRecommendationResponse;
}

function riskColor(level: string): string {
  switch (level.toLowerCase()) {
    case "low":
      return "text-success";
    case "medium":
      return "text-yellow-400";
    case "high":
      return "text-danger";
    default:
      return "text-text-secondary";
  }
}

function riskBorder(level: string): string {
  switch (level.toLowerCase()) {
    case "low":
      return "border-success/30 bg-success/10";
    case "medium":
      return "border-yellow-400/30 bg-yellow-400/10";
    case "high":
      return "border-danger/30 bg-danger/10";
    default:
      return "border-zinc-700/30 bg-zinc-800/10";
  }
}

function qualityBadgeStyle(quality: string): string {
  switch (quality.toLowerCase()) {
    case "high":
      return "border-success/30 bg-success/10 text-success";
    case "medium":
      return "border-yellow-400/30 bg-yellow-400/10 text-yellow-400";
    case "low":
      return "border-danger/30 bg-danger/10 text-danger";
    default:
      return "border-zinc-700/30 bg-zinc-800/10 text-text-secondary";
  }
}

function confidenceColor(value: number): string {
  if (value >= 80) return "bg-success";
  if (value >= 50) return "bg-yellow-400";
  return "bg-danger";
}

function confidenceTrackColor(value: number): string {
  if (value >= 80) return "bg-success/20";
  if (value >= 50) return "bg-yellow-400/20";
  return "bg-danger/20";
}

export function AIRecommendationCard({
  recommendation: r,
}: AIRecommendationCardProps) {
  const [openSections, setOpenSections] = useState<Set<string>>(
    new Set(["tempo", "energy", "compat"]),
  );

  if (!r?.summary) {
    return null;
  }

  const sections = [
    { id: "tempo", title: "Tempo Analysis", content: (
      <div className="grid gap-3 sm:grid-cols-2">
        <SubStat label="Difference" value={r.tempo_analysis.difference} />
        <SubStat label="Recommendation" value={r.tempo_analysis.recommendation} />
      </div>
    )},
    { id: "energy", title: "Energy Analysis", content: (
      <div className="grid gap-3 sm:grid-cols-2">
        <SubStat label="Difference" value={r.energy_analysis.difference} />
        <SubStat label="Recommendation" value={r.energy_analysis.recommendation} />
      </div>
    )},
    { id: "compat", title: "Compatibility Analysis", content: (
      <div className="grid gap-3 sm:grid-cols-2">
        <SubStat label="Score" value={r.compatibility_analysis.score} />
        <SubStat label="Interpretation" value={r.compatibility_analysis.interpretation} />
      </div>
    )},
    { id: "strategy", title: "Mix Strategy", content: (
      <div className="grid gap-3 sm:grid-cols-3">
        <SubStat label="Before Transition" value={r.mix_strategy.before_transition} />
        <SubStat label="During Transition" value={r.mix_strategy.during_transition} />
        <SubStat label="After Transition" value={r.mix_strategy.after_transition} />
      </div>
    )},
    { id: "exec", title: "DJ Execution", content: (
      <div className="grid gap-3 sm:grid-cols-3">
        <SubStat label="Loop" value={r.dj_execution.loop} />
        <SubStat label="EQ" value={r.dj_execution.eq} />
        <SubStat label="Filter" value={r.dj_execution.filter} />
        <SubStat label="Tempo Fader" value={r.dj_execution.tempo_fader} />
        <SubStat label="Phrase Matching" value={r.dj_execution.phrase_matching} />
        <SubStat label="Cue Point" value={r.dj_execution.cue_point} />
      </div>
    )},
    { id: "risks", title: "Risks", content: r.risks.length > 0 ? (
      <ul className="space-y-2">
        {r.risks.map((risk, i) => (
          <li key={i} className="flex items-start gap-2 rounded-xl border border-danger/20 bg-danger/5 px-4 py-2 text-sm text-red-200">
            <span className="mt-0.5 shrink-0 text-danger">&#9679;</span>
            {risk}
          </li>
        ))}
      </ul>
    ) : null},
    { id: "club", title: "Club Tip", content: r.club_tip ? (
      <div className="rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm text-primary">
        {r.club_tip}
      </div>
    ) : null},
    { id: "notes", title: "Professional Notes", content: r.professional_notes ? (
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3 text-sm text-text-secondary">
        {r.professional_notes}
      </div>
    ) : null},
    { id: "use_case", title: "Best Use Case", content: r.best_use_case ? (
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3 text-sm font-medium text-text">
        {r.best_use_case}
      </div>
    ) : null},
  ].filter((s) => s.content !== null);

  function toggle(id: string) {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <section className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7">
      {/* Header */}
      <header className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-text">AI Recommendation</h3>
          <span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wider ${riskColor(r.risk_level)} ${riskBorder(r.risk_level)}`}>
            {r.risk_level} Risk
          </span>
        </div>
        {r.ai_model && (
          <span className="flex items-center gap-1.5 rounded-full border border-zinc-700/40 bg-zinc-800/40 px-3 py-1 text-[11px] text-text-secondary">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            {r.ai_model.split("/").pop()}
          </span>
        )}
      </header>

      {/* Summary */}
      <div className="mb-5 rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3">
        <p className="text-sm font-medium italic leading-relaxed text-text">{r.summary}</p>
      </div>

      {/* Confidence bar */}
      <div className="mb-5">
        <div className="mb-1.5 flex items-center justify-between text-xs text-text-secondary">
          <span>Confidence</span>
          <span className={`font-semibold ${confidenceColor(r.confidence).replace("bg-", "text-")}`}>
            {r.confidence}%
          </span>
        </div>
        <div className={`h-2 w-full overflow-hidden rounded-full ${confidenceTrackColor(r.confidence)}`}>
          <div
            className={`h-full rounded-full transition-all duration-700 ${confidenceColor(r.confidence)}`}
            style={{ width: `${r.confidence}%` }}
          />
        </div>
      </div>

      {/* Quick stats */}
      <div className="mb-5 grid gap-3 sm:grid-cols-3">
        <Stat label="Mix Direction" value={r.mix_direction} />
        <Stat
          label="Transition Quality"
          value={r.transition_quality}
          badge
          badgeClass={qualityBadgeStyle(r.transition_quality)}
        />
        <Stat label="Transition Type" value={r.transition_type} />
      </div>

      {/* Accordion sections */}
      <div className="space-y-3">
        {sections.map((s) => (
          <AccordionSection
            key={s.id}
            title={s.title}
            open={openSections.has(s.id)}
            onToggle={() => toggle(s.id)}
          >
            {s.content}
          </AccordionSection>
        ))}
      </div>

      {/* Model info */}
      <div className="mt-4 flex flex-wrap items-center justify-end gap-2 text-[11px] text-text-secondary/50">
        {r.ai_model && (
          <span className="flex items-center gap-1">
            Generated by {r.ai_model.split("/").pop()}
          </span>
        )}
        {r.ai_latency != null && (
          <>
            <span className="text-text-secondary/20">|</span>
            <span>{r.ai_latency.toFixed(1)} s</span>
          </>
        )}
        {r.ai_retry_count != null && (
          <>
            <span className="text-text-secondary/20">|</span>
            <span>Retry: {r.ai_retry_count}</span>
          </>
        )}
        {r.ai_fallback_occurred != null && (
          <>
            <span className="text-text-secondary/20">|</span>
            <span className={r.ai_fallback_occurred ? "text-danger/60" : ""}>
              Fallback: {r.ai_fallback_occurred ? "Yes" : "No"}
            </span>
          </>
        )}
        {r.ai_provider && (
          <>
            <span className="text-text-secondary/20">|</span>
            <span>{r.ai_provider}</span>
          </>
        )}
      </div>
    </section>
  );
}

// -----------------------------------------------------------------------
// Sub-components
// -----------------------------------------------------------------------

function AccordionSection({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between bg-zinc-900/65 px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary transition hover:bg-zinc-900"
      >
        {title}
        <svg
          className={`h-4 w-4 shrink-0 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div
        className={`transition-all duration-200 ${open ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"}`}
      >
        <div className="px-4 pb-4 pt-3">{children}</div>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  badge,
  badgeClass,
}: {
  label: string;
  value: string;
  badge?: boolean;
  badgeClass?: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.15em] text-text-secondary">{label}</p>
      {badge ? (
        <span className={`mt-1.5 inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold ${badgeClass ?? "text-text"}`}>
          {value}
        </span>
      ) : (
        <p className="mt-1 text-base font-semibold text-text">{value}</p>
      )}
    </div>
  );
}

function SubStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.13em] text-text-secondary">{label}</p>
      <p className="mt-1 text-sm leading-relaxed text-text">{value}</p>
    </div>
  );
}
