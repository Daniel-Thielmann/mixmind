"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import type { TransitionAnalysis } from "@/types/transition-analysis";

interface TransitionTimelineProps {
  analysis: TransitionAnalysis;
  currentTime: number;
  duration: number;
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

export function TransitionTimeline({
  analysis,
  currentTime,
  duration,
}: TransitionTimelineProps) {
  const progress = Math.min(currentTime / duration, 1);

  const activeRegion = analysis.regions.find(
    (r) => currentTime >= r.startTime && currentTime < r.endTime,
  );

  const trackColors = useMemo(
    () => ({
      a: analysis.tracks.a.color,
      b: analysis.tracks.b.color,
    }),
    [analysis],
  );

  return (
    <div className="select-none space-y-4">
      <div className="flex items-center justify-between text-[13px]">
        <span className="font-medium text-zinc-400">Transition Timeline</span>
        <span className="font-mono tabular-nums text-zinc-600">
          {formatTime(currentTime)}
        </span>
      </div>

      {/* Track color legend */}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs">
        <div className="flex items-center gap-1.5">
          <div
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: trackColors.a }}
          />
          <span className="text-zinc-500">{analysis.tracks.a.name}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: trackColors.b }}
          />
          <span className="text-zinc-500">{analysis.tracks.b.name}</span>
        </div>
      </div>

      {/* Timeline bar */}
      <div className="relative h-11 overflow-hidden rounded-xl bg-zinc-900/60">
        {analysis.regions.map((region, i) => {
          const left = (region.startTime / duration) * 100;
          const width = ((region.endTime - region.startTime) / duration) * 100;
          const isActive =
            currentTime >= region.startTime && currentTime < region.endTime;
          const isPast = currentTime >= region.endTime;

          return (
            <div
              key={i}
              className="absolute inset-y-0 transition-all duration-300"
              style={{
                left: `${left}%`,
                width: `${width}%`,
                backgroundColor: region.color,
                opacity: isActive ? 0.2 : isPast ? 0.06 : 0.04,
                borderRight:
                  i < analysis.regions.length - 1
                    ? "1px solid rgba(255,255,255,0.03)"
                    : undefined,
              }}
            />
          );
        })}

        {/* Region labels inside bar */}
        {analysis.regions.map((region, i) => {
          const left = (region.startTime / duration) * 100;
          const width = ((region.endTime - region.startTime) / duration) * 100;
          const isActive =
            currentTime >= region.startTime && currentTime < region.endTime;

          if (width < 8) return null;

          return (
            <div
              key={`label-${i}`}
              className="absolute inset-y-0 flex items-center justify-center"
              style={{ left: `${left}%`, width: `${width}%` }}
            >
              <span
                className={`whitespace-nowrap px-1 text-[10px] font-semibold uppercase tracking-wider transition-colors ${
                  isActive ? "text-white" : "text-zinc-600"
                }`}
              >
                {region.label}
              </span>
            </div>
          );
        })}

        {/* Playhead */}
        <motion.div
          className="absolute inset-y-0 z-10"
          style={{ left: `${progress * 100}%` }}
          transition={{ duration: 0.15, ease: "linear" }}
        >
          <div className="absolute inset-y-0 left-0 w-px bg-gradient-to-b from-primary/60 via-primary to-primary/60 shadow-sm shadow-primary/30" />
          <div className="absolute -left-1.5 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-primary shadow-sm shadow-primary/50" />
        </motion.div>
      </div>

      {/* Active region label */}
      <div className="flex items-center justify-between text-xs">
        <motion.span
          key={activeRegion?.label ?? "start"}
          initial={{ opacity: 0, y: -2 }}
          animate={{ opacity: 1, y: 0 }}
          className="font-medium"
          style={{ color: activeRegion?.color ?? trackColors.a }}
        >
          {activeRegion?.label ?? analysis.tracks.a.name}
        </motion.span>
        <span className="text-zinc-600">
          {activeRegion
            ? `${formatTime(activeRegion.startTime)} — ${formatTime(activeRegion.endTime)}`
            : `0:00 — ${formatTime(duration)}`}
        </span>
      </div>
    </div>
  );
}
