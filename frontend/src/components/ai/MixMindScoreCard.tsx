"use client";

import { motion } from "framer-motion";
import type { AIRecommendationResponse, CompatibilityResult } from "@/types";

interface MixMindScoreCardProps {
  recommendation: AIRecommendationResponse;
  compatibility: CompatibilityResult;
}

function scoreColor(score: number) {
  if (score >= 80) return { hex: "#21d969", label: "Excellent Transition" };
  if (score >= 60) return { hex: "#facc15", label: "Good Transition" };
  if (score >= 40) return { hex: "#fb923c", label: "Fair Transition" };
  return { hex: "#ff5b6e", label: "Challenging Transition" };
}

export function MixMindScoreCard({
  recommendation: r,
  compatibility,
}: MixMindScoreCardProps) {
  const score = r.dj_score;
  const { hex, label } = scoreColor(score);
  const size = 120;
  const stroke = 8;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
        MixMind Score
      </h3>

      <div className="flex flex-wrap items-center gap-6">
        <div className="relative inline-flex items-center justify-center shrink-0">
          <motion.svg
            width={size}
            height={size}
            className="-rotate-90"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth={stroke}
            />
            <motion.circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={hex}
              strokeWidth={stroke}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 1.2, ease: "easeOut" }}
            />
          </motion.svg>
          <motion.span
            className="absolute text-2xl font-bold tracking-tight"
            style={{ color: hex }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, duration: 0.4 }}
          >
            {score}
          </motion.span>
        </div>

        <div className="flex flex-col gap-1">
          <span
            className="text-lg font-semibold"
            style={{ color: hex }}
          >
            {label}
          </span>
          <span className="text-xs text-text-secondary">
            Based on {compatibility.compatibility_score.toFixed(0)}% compatibility score
          </span>
        </div>
      </div>

      <div className="mt-4 h-2 rounded-full bg-zinc-800">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: hex }}
          initial={{ width: "0%" }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
        />
      </div>
    </motion.section>
  );
}
