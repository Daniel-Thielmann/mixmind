"use client";

import { motion } from "framer-motion";
import {
  Radio,
  Waves,
  Filter,
  Timer,
  Music,
  Disc3,
} from "lucide-react";
import type { DJExecution } from "@/types";

interface DJExecutionTimelineProps {
  execution: DJExecution;
}

const STEP_ICONS = [
  { key: "cue_point", icon: Radio, label: "Cue" },
  { key: "loop", icon: Waves, label: "Loop" },
  { key: "eq", icon: Filter, label: "EQ" },
  { key: "filter", icon: Timer, label: "Filter" },
  { key: "tempo_fader", icon: Music, label: "Tempo" },
  { key: "phrase_matching", icon: Disc3, label: "Release" },
] as const;

export function DJExecutionTimeline({ execution }: DJExecutionTimelineProps) {
  const steps = STEP_ICONS.map((s) => ({
    ...s,
    // Controle caso IA indisponível
    value: execution[s.key as keyof DJExecution] || "Manual control required.",
  }));

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      // Blindagem do layout
      className="relative z-0 overflow-hidden rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
        DJ Execution Timeline
      </h3>

      <div className="space-y-0 relative z-10">
        {steps.map((step, i) => (
          <div key={step.key} className="relative flex gap-4 pb-6 last:pb-0">
            {i < steps.length - 1 && (
              <div className="absolute left-[15px] top-7 bottom-0 w-px bg-cyan-900/40" />
            )}
            <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-cyan-800/50 bg-cyan-950/30 shadow-[0_0_10px_rgba(34,211,238,0.2)]">
              {/* Ícones glowing */}
              <step.icon className="h-4 w-4 text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]" />
            </div>
            <div className="min-w-0 flex-1 pt-0.5">
              <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                {step.label}
              </span>
              <p className="mt-1 text-sm leading-relaxed text-text/80 break-normal">
                {step.value}
              </p>
            </div>
          </div>
        ))}
      </div>
    </motion.section>
  );
}