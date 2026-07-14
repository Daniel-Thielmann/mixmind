"use client";

import { motion } from "framer-motion";
import type { AIRecommendationResponse, CompatibilityResult } from "@/types";

interface HeatIndicatorsProps {
  recommendation: AIRecommendationResponse;
  compatibility: CompatibilityResult;
}

// Conversão da Camelot Whell para representar na barra de progresso
function getHarmonicScore(match: string | undefined): number {
  if (!match) return 0;
  const lowerMatch = match.toLowerCase();
  
  if (lowerMatch.includes("perfect")) return 100;
  if (lowerMatch.includes("excellent")) return 90;
  if (lowerMatch.includes("very good")) return 85;
  if (lowerMatch.includes("good")) return 80;
  if (lowerMatch.includes("compatible")) return 75;
  if (lowerMatch.includes("fair")) return 50;
  if (lowerMatch.includes("clash")) return 20;
  
  return 0;
}

function Bar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-28 text-xs uppercase tracking-[0.13em] text-text-secondary shrink-0">
        {label}
      </span>
      <div className="flex-1 h-2.5 rounded-full bg-zinc-800 overflow-hidden">
        <motion.div
          className="h-full rounded-full drop-shadow-[0_0_8px_rgba(34,211,238,0.2)]"
          style={{ backgroundColor: color }}
          initial={{ width: "0%" }}
          animate={{ width: `${Math.max(0, Math.min(value, 100))}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
      <span className="w-8 text-right text-xs font-semibold text-text">
        {Math.round(Math.max(0, Math.min(value, 100)))}
      </span>
    </div>
  );
}

export function HeatIndicators({
  recommendation: r,
  compatibility,
}: HeatIndicatorsProps) {
  // Fallback seguro caso risk_level venha vazio
  const riskScore =
    r.risk_level?.toLowerCase() === "low"
      ? 20
      : r.risk_level?.toLowerCase() === "medium"
        ? 50
        : r.risk_level ? 85 : 20; // Default fallback

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
          value={compatibility.compatibility_score || 0}
          color="#22d3ee" 
        />
        <Bar
          label="Energy"
          value={100 - (compatibility.energy_difference || 0) * 500}
          color="#21d969" 
        />
        <Bar
          label="Harmony"
          value={getHarmonicScore(compatibility.harmonic_match)}
          color="#22d3ee" 
        />
        <Bar
          label="Compatibility"
          value={compatibility.compatibility_score || 0}
          color="#22d3ee" 
        />
        <Bar
          label="Confidence"
          value={r.confidence || 0}
          color={(r.confidence || 0) >= 80 ? "#21d969" : (r.confidence || 0) >= 50 ? "#facc15" : "#ff5b6e"}
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