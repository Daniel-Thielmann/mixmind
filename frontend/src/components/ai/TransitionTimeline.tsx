"use client";

import { motion } from "framer-motion";
import { ArrowDown, Disc3 } from "lucide-react";

interface TransitionTimelineProps {
  transitionType: string;
  transitionQuality: string;
  transitionLength: string;
}

export function TransitionTimeline({
  transitionType,
  transitionQuality,
  transitionLength,
}: TransitionTimelineProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
        Transition Timeline
      </h3>

      <div className="flex items-center justify-between gap-2">
        <Step icon={<Disc3 className="h-5 w-5 text-primary" />} label="Track A" color="text-primary" />

        <div className="flex flex-1 items-center gap-1">
          <div className="h-px flex-1 bg-zinc-700" />
          <ArrowDown className="h-4 w-4 text-text-secondary" />
          <div className="h-px flex-1 bg-zinc-700" />
        </div>

        <Step
          icon={<span className="text-xs font-bold text-yellow-400">S</span>}
          label="Transition Start"
          color="text-yellow-400"
        />

        <div className="flex flex-1 items-center gap-1">
          <div className="h-px flex-1 bg-zinc-700" />
          <ArrowDown className="h-4 w-4 text-text-secondary" />
          <div className="h-px flex-1 bg-zinc-700" />
        </div>

        <Step
          icon={<span className="text-xs font-bold text-primary">B</span>}
          label={transitionType}
          color="text-primary"
          sub={`${transitionQuality} · ${transitionLength}`}
        />

        <div className="flex flex-1 items-center gap-1">
          <div className="h-px flex-1 bg-zinc-700" />
          <ArrowDown className="h-4 w-4 text-text-secondary" />
          <div className="h-px flex-1 bg-zinc-700" />
        </div>

        <Step
          icon={<span className="text-xs font-bold text-danger">E</span>}
          label="Transition End"
          color="text-danger"
        />

        <div className="flex flex-1 items-center gap-1">
          <div className="h-px flex-1 bg-zinc-700" />
          <ArrowDown className="h-4 w-4 text-text-secondary" />
          <div className="h-px flex-1 bg-zinc-700" />
        </div>

        <Step icon={<Disc3 className="h-5 w-5 text-primary" />} label="Track B" color="text-primary" />
      </div>
    </motion.section>
  );
}

function Step({
  icon,
  label,
  color,
  sub,
}: {
  icon: React.ReactNode;
  label: string;
  color: string;
  sub?: string;
}) {
  return (
    <div className="flex shrink-0 flex-col items-center gap-1 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full border border-zinc-700 bg-zinc-900/80">
        {icon}
      </div>
      <span className={`text-[10px] font-semibold uppercase tracking-wider ${color}`}>
        {label}
      </span>
      {sub && (
        <span className="text-[8px] text-text-secondary/50 max-w-16 leading-tight">
          {sub}
        </span>
      )}
    </div>
  );
}
