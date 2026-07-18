"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { TransitionAnalysis } from "@/types/transition-analysis";

interface LiveCommentaryProps {
  analysis: TransitionAnalysis;
  currentTime: number;
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
}

export function LiveCommentary({
  analysis,
  currentTime,
}: LiveCommentaryProps) {
  const currentEvent = useMemo(() => {
    const tolerance = 2;
    const active = analysis.events.find(
      (e) => Math.abs(currentTime - e.time) <= tolerance,
    );
    if (active) return active;

    const past = [...analysis.events]
      .reverse()
      .find((e) => currentTime >= e.time + tolerance);
    return past ?? null;
  }, [currentTime, analysis.events]);

  return (
    <div className="space-y-4">
      <p className="text-[13px] font-medium text-zinc-400">Live Commentary</p>
      <div className="relative min-h-32">
        <AnimatePresence mode="wait">
          {currentEvent ? (
            <motion.div
              key={currentEvent.time}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
              className="absolute inset-0"
            >
              <div className="flex min-h-32 flex-col justify-center rounded-xl border border-zinc-800 bg-zinc-900/40 px-5 py-4">
                <span className="font-mono text-xs font-medium text-primary">
                  {formatTime(currentEvent.time)}
                </span>
                <p className="mt-2 text-sm leading-relaxed text-zinc-300">
                  {currentEvent.description}
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="waiting"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute inset-0 flex items-center justify-center rounded-lg border border-dashed border-zinc-800"
            >
              <span className="text-sm text-zinc-600">
                Waiting for transition start...
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
