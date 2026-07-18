"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { TransitionAnalysis } from "@/types/transition-analysis";

interface AIFocusProps {
  analysis: TransitionAnalysis;
  currentTime: number;
}

const FOCUS_MAP: Record<
  string,
  { icon: string; label: string }
> = {
  "track-a": { icon: "🎵", label: "Analyzing Track A" },
  "build-up": { icon: "↗", label: "Build-Up In Progress" },
  "phrase-match": { icon: "🥁", label: "Phrase Match Confirmed" },
  "eq-blend": { icon: "🎚", label: "EQ Blend in Progress" },
  "bass-transfer": { icon: "⚡", label: "Bass Transfer Detected" },
  "peak-harmony": { icon: "🔥", label: "Peak Harmonic Compatibility" },
  "track-b": { icon: "🎵", label: "Track B Taking Over" },
};

export function AIFocus({ analysis, currentTime }: AIFocusProps) {
  const activeRegion = useMemo(
    () =>
      analysis.regions.find(
        (r) => currentTime >= r.startTime && currentTime < r.endTime,
      ),
    [currentTime, analysis.regions],
  );

  const focus = activeRegion
    ? FOCUS_MAP[activeRegion.type] ?? { icon: "●", label: "Analyzing..." }
    : { icon: "●", label: "Waiting..." };

  return (
    <div className="space-y-4">
      <p className="text-[13px] font-medium text-zinc-400">AI Focus</p>
      <div className="relative flex min-h-32 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900/20">
        <AnimatePresence mode="wait">
          <motion.div
            key={focus.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.25 }}
            className="flex flex-col items-center gap-3 px-5 py-5 text-center"
          >
            <span className="text-3xl">{focus.icon}</span>
            <span className="text-sm font-medium text-zinc-200">
              {focus.label}
            </span>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
