"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";

interface AudioPlayerProps {
  label: string;
  trackTitle: string;
  color: string;
}

export function AudioPlayer({ label, trackTitle, color }: AudioPlayerProps) {
  const barHeights = useMemo(() =>
    Array.from({ length: 32 }, (_, i) => ((i * 17 + 3) % 24) + 4),
  []);

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border bg-card p-6 transition-all duration-500 hover:border-border-light hover:bg-card-hover">
      <div className="mb-3 flex items-center justify-between">
        <span className={`text-xs font-semibold uppercase tracking-[0.2em] ${color}`}>
          {label}
        </span>
        <span className="text-xs text-text-tertiary">0:00 / 3:05</span>
      </div>
      <p className="mb-4 text-sm font-medium text-text">{trackTitle}</p>
      <div className="mb-3 flex items-center gap-3">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20 text-primary transition-colors hover:bg-primary/30"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5,3 19,12 5,21" />
          </svg>
        </motion.button>
        <div className="relative h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{ background: `linear-gradient(90deg, ${color === "text-primary" ? "#44f3d0" : "#3b82f6"}, ${color === "text-primary" ? "#2bc9a8" : "#8b5cf6"})` }}
            initial={{ width: "0%" }}
            whileHover={{ width: "45%" }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
      </div>
      <div className="flex items-center gap-1.5">
        {barHeights.map((h, i) => (
          <motion.div
            key={i}
            className="flex-1 rounded-full"
            style={{
              background: `linear-gradient(to top, ${color === "text-primary" ? "#44f3d0" : "#3b82f6"}, ${color === "text-primary" ? "#2bc9a8" : "#8b5cf6"})`,
            }}
            initial={{ height: 4 }}
            whileHover={{ height: h, transition: { duration: 0.3 } }}
          />
        ))}
      </div>
    </div>
  );
}