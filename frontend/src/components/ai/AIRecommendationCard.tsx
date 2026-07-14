"use client";

import { motion } from "framer-motion";
import {
  Sparkles,
  Route,
  Gauge,
  Zap,
  Layers,
  Users,
  Lightbulb,
  StickyNote,
  Swords,
  Target,
} from "lucide-react";
import type { AIRecommendationResponse } from "@/types";
import { RiskBadge } from "./RiskBadge";

interface AIRecommendationCardProps {
  recommendation: AIRecommendationResponse;
}

export function AIRecommendationCard({
  recommendation: r,
}: AIRecommendationCardProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.35 }}
      className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-text">AI Recommendation</h3>
        <RiskBadge level={r.risk_level || "Unknown"} />
      </div>

      <Block icon={Sparkles} title="Summary">
        <p className="rounded-xl border border-primary/10 bg-primary/2 px-5 py-4 text-sm font-medium italic leading-relaxed text-text/90">
          {r.summary || "AI summary generation pending or unavailable."}
        </p>
      </Block>

      <Block icon={Route} title="Mix Direction">
        <Stat value={r.mix_direction || "Review the transition manually before mixing."} />
      </Block>

      <Block icon={Gauge} title="Tempo Analysis">
        <div
          className="grid gap-4"
          style={{
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          }}
        >
          <MiniStat label="Difference" value={r.tempo_analysis?.difference || "N/A"} />
          <MiniStat label="Recommendation" value={r.tempo_analysis?.recommendation || "N/A"} />
        </div>
      </Block>

      <Block icon={Zap} title="Energy Analysis">
        <div
          className="grid gap-4"
          style={{
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          }}
        >
          <MiniStat label="Difference" value={r.energy_analysis?.difference || "N/A"} />
          <MiniStat label="Recommendation" value={r.energy_analysis?.recommendation || "N/A"} />
        </div>
      </Block>

      <Block icon={Layers} title="Mix Strategy">
        <div
          className="grid gap-4"
          style={{
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          }}
        >
          <MiniStat label="Before" value={r.mix_strategy?.before_transition || "Prepare tracks."} />
          <MiniStat label="During" value={r.mix_strategy?.during_transition || "Execute blend."} />
          <MiniStat label="After" value={r.mix_strategy?.after_transition || "Monitor levels."} />
        </div>
      </Block>

      <Block icon={Swords} title="Risks">
        {r.risks && r.risks.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {r.risks.map((risk, i) => (
              <span
                key={i}
                className="rounded-full border border-danger/20 bg-danger/10 px-3 py-1 text-xs font-medium text-danger"
              >
                {risk}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-text-secondary">No risks identified.</p>
        )}
      </Block>

      <Block icon={Lightbulb} title="Club Tip" condition={!!r.club_tip}>
        {r.club_tip && (
          <p className="rounded-xl border border-success/15 bg-success/3 px-5 py-4 text-sm leading-relaxed text-success/90">
            {r.club_tip}
          </p>
        )}
      </Block>

      <Block icon={StickyNote} title="Professional Notes" condition={!!r.professional_notes}>
        {r.professional_notes && (
          <p className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-5 py-4 text-sm leading-relaxed text-text-secondary">
            {r.professional_notes}
          </p>
        )}
      </Block>

      <div
        className="grid gap-4"
        style={{
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        }}
      >
        {r.best_use_case && (
          <Block icon={Target} title="Best Use Case">
            <Stat value={r.best_use_case} />
          </Block>
        )}
        {r.alternative_strategy && (
          <Block icon={Route} title="Alternative Strategy">
            <Stat value={r.alternative_strategy} />
          </Block>
        )}
      </div>

      {r.why_this_strategy && (
        <div className="mt-5">
          <Block icon={Users} title="Why This Strategy">
            <Stat value={r.why_this_strategy} />
          </Block>
        </div>
      )}
    </motion.section>
  );
}

function Block({
  icon: Icon,
  title,
  children,
  condition = true,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  children: React.ReactNode;
  condition?: boolean;
}) {
  if (!condition) return null;
  return (
    <div className="mb-5 last:mb-0">
      <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.3)]">
        <Icon className="h-3.5 w-3.5 shrink-0" />
        {title}
      </h4>
      {children}
    </div>
  );
}

function Stat({ value }: { value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-5 py-4">
      <p className="text-sm leading-relaxed text-text whitespace-normal">
        {value}
      </p>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/65 px-5 py-4">
      <p className="mb-2 text-xs uppercase tracking-[0.15em] text-text-secondary">
        {label}
      </p>
      <p className="text-sm leading-relaxed text-text whitespace-normal">
        {value}
      </p>
    </div>
  );
}