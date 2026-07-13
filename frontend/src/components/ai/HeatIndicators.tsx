"use client";

import { motion } from "framer-motion";
import type { AIRecommendationResponse, CompatibilityResult } from "@/types";

interface HeatIndicatorsProps {
  recommendation: AIRecommendationResponse;
  compatibility: CompatibilityResult;
}

function Bar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-28 text-xs uppercase tracking-[0.13em] text-text-secondary shrink-0">
        {label}
      </span>
      <div className="flex-1 h-2.5 rounded-full bg-zinc-800 overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: "0%" }}
          animate={{ width: `${Math.min(value, 100)}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
      <span className="w-8 text-right text-xs font-semibold text-text">
        {Math.round(Math.min(value, 100))}
      </span>
    </div>
  );
}

export function HeatIndicators({
  recommendation: r,
  compatibility,
}: HeatIndicatorsProps) {
  const riskScore =
    r.risk_level.toLowerCase() === "low"
      ? 20
      : r.risk_level.toLowerCase() === "medium"
        ? 50
        : 85;

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.25 }}
      className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
        Metrics Overview
      </h3>

      <div className="space-y-3">
        <Bar
          label="Tempo"
          value={Math.min(compatibility.compatibility_score, 100)}
          color="#44f3d0"
        />
        <Bar
          label="Energy"
          value={Math.min(100 - compatibility.energy_difference * 500, 100)}
          color="#21d969"
        />
        <Bar
          label="Compatibility"
          value={compatibility.compatibility_score}
          color="#44f3d0"
        />
        <Bar
          label="Confidence"
          value={r.confidence}
          color={r.confidence >= 80 ? "#21d969" : r.confidence >= 50 ? "#facc15" : "#ff5b6e"}
        />
        <Bar
          label="Risk"
          value={riskScore}
          color={riskScore <= 30 ? "#21d969" : riskScore <= 60 ? "#facc15" : "#ff5b6e"}
        />
      </div>
    </motion.section>
  );
}
