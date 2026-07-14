"use client";

import { motion } from "framer-motion";
import {
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from "recharts";
import type { AIRecommendationResponse, CompatibilityResult } from "@/types";

interface RadarChartProps {
  recommendation: AIRecommendationResponse;
  compatibility: CompatibilityResult;
}

// Harmonia convertida em pontuação numérica para apresentção no chart 
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

export function RadarChartCard({
  recommendation: r,
  compatibility,
}: RadarChartProps) {
  // Ajuste de segurança caso r.risk_level venha indefinido no fallback
  const riskScore =
    r.risk_level?.toLowerCase() === "low"
      ? 80
      : r.risk_level?.toLowerCase() === "medium"
        ? 50
        : 20;

  // Inserindo a Harmonia (Hexágono agora)
  const data = [
    { axis: "Tempo", value: Math.min(compatibility.compatibility_score || 0, 100) },
    { axis: "Energy", value: Math.max(0, Math.min(100 - (compatibility.energy_difference || 0) * 500, 100)) },
    { axis: "Harmony", value: getHarmonicScore(compatibility.harmonic_match) },
    { axis: "Compatibility", value: compatibility.compatibility_score || 0 },
    { axis: "Confidence", value: r.confidence || 0 },
    { axis: "Risk", value: riskScore },
  ];

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
        Analysis Overview
      </h3>

      <ResponsiveContainer width="100%" height={380}>
        <RechartsRadar data={data} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid stroke="rgba(255,255,255,0.08)" />
          <PolarAngleAxis
            dataKey="axis"
            tick={{ fill: "#98a4b7", fontSize: 11 }}
            axisLine={false}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="#22d3ee" 
            fill="#22d3ee"
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </motion.section>
  );
}