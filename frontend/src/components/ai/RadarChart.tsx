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

export function RadarChartCard({
  recommendation: r,
  compatibility,
}: RadarChartProps) {
  const riskScore =
    r.risk_level.toLowerCase() === "low"
      ? 80
      : r.risk_level.toLowerCase() === "medium"
        ? 50
        : 20;

  const data = [
    { axis: "Tempo", value: Math.min(compatibility.compatibility_score, 100) },
    { axis: "Energy", value: Math.min(100 - compatibility.energy_difference * 500, 100) },
    { axis: "Compatibility", value: compatibility.compatibility_score },
    { axis: "Confidence", value: r.confidence },
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

      <ResponsiveContainer width="100%" height={280}>
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
            stroke="#44f3d0"
            fill="#44f3d0"
            fillOpacity={0.15}
            strokeWidth={2}
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </motion.section>
  );
}
