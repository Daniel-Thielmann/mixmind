"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

const STEPS = [
  { label: "Analyzing BPM…", icon: "🎵" },
  { label: "Matching Harmonic Keys…", icon: "🎹" },
  { label: "Finding Phrase Alignment…", icon: "📐" },
  { label: "Calculating Energy Curve…", icon: "⚡" },
  { label: "Building Transition…", icon: "✨" },
];

interface ProcessingPipelineProps {
  onComplete: () => void;
}

export function ProcessingPipeline({ onComplete }: ProcessingPipelineProps) {
  const [step, setStep] = useState(0);

  const advance = useCallback(() => {
    setStep((s) => {
      if (s >= STEPS.length - 1) {
        setTimeout(() => onComplete(), 600);
        return s;
      }
      return s + 1;
    });
  }, [onComplete]);

  useEffect(() => {
    const t = setTimeout(advance, 700 + Math.random() * 400);
    return () => clearTimeout(t);
  }, [step, advance]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className="mx-auto max-w-md"
    >
      <div className="relative overflow-hidden rounded-2xl border border-primary/15 bg-card/80 p-6 backdrop-blur-sm">
        <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-b from-primary/[0.04] to-transparent" />
        <div className="pointer-events-none absolute -inset-4 rounded-3xl bg-primary/5 blur-2xl" />

        <div className="relative">
          <div className="mb-5 text-center">
            <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="h-5 w-5 rounded-full border-2 border-primary border-t-transparent"
              />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">AI Processing</p>
          </div>

          <div className="space-y-3">
            {STEPS.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, x: -12 }}
                animate={{
                  opacity: i <= step ? 1 : 0.25,
                  x: i <= step ? 0 : -8,
                }}
                transition={{ duration: 0.3 }}
                className="flex items-center gap-3"
              >
                <div
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] transition-all duration-500 ${
                    i < step
                      ? "bg-primary/20 text-primary"
                      : i === step
                        ? "bg-primary text-background"
                        : "bg-zinc-800 text-text-tertiary"
                  }`}
                >
                  {i < step ? (
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : i === step ? (
                    <motion.div
                      animate={{ scale: [1, 1.25, 1] }}
                      transition={{ duration: 0.8, repeat: Infinity }}
                      className="h-1.5 w-1.5 rounded-full bg-current"
                    />
                  ) : (
                    <span className="text-[9px]">{i + 1}</span>
                  )}
                </div>
                <span className={`text-xs transition-colors duration-300 ${i <= step ? "text-text" : "text-text-tertiary"}`}>
                  {s.label}
                </span>
              </motion.div>
            ))}
          </div>

          {step >= STEPS.length - 1 && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 text-center text-[11px] text-primary"
            >
              Preview ready ✓
            </motion.p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
