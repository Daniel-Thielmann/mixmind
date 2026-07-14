"use client";

import { motion } from "framer-motion";
import { CheckCircle2, AlertTriangle } from "lucide-react";
import type { CompatibilityResult } from "@/types";

interface WhyThisScoreProps {
  compatibility: CompatibilityResult;
}

export function WhyThisScore({ compatibility }: WhyThisScoreProps) {
  const factors = [
    {
      label: "Tempo Match",
      value: compatibility.tempo_match,
      good: ["Excellent", "Very Good", "Good"].includes(compatibility.tempo_match),
    },
    {
      label: "Energy Match",
      value: compatibility.energy_match,
      good: ["Excellent", "Very Good", "Good"].includes(compatibility.energy_match),
    },
    {
      label: "Harmonic Match",
      value: compatibility.harmonic_match || "N/A",
      good: ["Perfect", "Excellent", "Very Good", "Good", "Compatible"].includes(
        compatibility.harmonic_match || ""
      ),
    },
    {
      label: "Overall Rating",
      value: compatibility.overall_rating,
      good: ["Excellent", "Very Good", "Good"].includes(compatibility.overall_rating),
    },
  ];

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
        Why This Score?
      </h3>

      <div className="space-y-3">
        {factors.map((factor) => (
          <div
            key={factor.label}
            className="flex items-center gap-3 rounded-xl border border-zinc-800 bg-zinc-900/65 px-4 py-3"
          >
            {factor.good ? (
              <CheckCircle2 className="h-5 w-5 shrink-0 text-success" />
            ) : (
              <AlertTriangle className="h-5 w-5 shrink-0 text-yellow-400" />
            )}
            <div className="flex flex-1 items-center justify-between gap-2">
              <span className="text-xs uppercase tracking-[0.13em] text-text-secondary">
                {factor.label}
              </span>
              <span
                className={`text-sm font-semibold ${
                  factor.good ? "text-success" : "text-yellow-400"
                }`}
              >
                {factor.value}
              </span>
            </div>
          </div>
        ))}
      </div>
    </motion.section>
  );
}
