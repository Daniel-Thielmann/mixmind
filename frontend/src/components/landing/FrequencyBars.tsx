"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";

interface FrequencyBarsProps {
  playing: boolean;
  color?: string;
  barCount?: number;
}

export function FrequencyBars({ playing, color = "#44f3d0", barCount = 48 }: FrequencyBarsProps) {
  const [heights, setHeights] = useState<number[]>(() =>
    Array.from({ length: barCount }, () => 8)
  );
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const resetHeights = useCallback(() => {
    setHeights(Array.from({ length: barCount }, () => 8));
  }, [barCount]);

  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        setHeights(
          Array.from({ length: barCount }, () => Math.random() * 48 + 4)
        );
      }, 100);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [playing, barCount]);

  useEffect(() => {
    if (!playing) {
      const id = requestAnimationFrame(() => resetHeights());
      return () => cancelAnimationFrame(id);
    }
  }, [playing, resetHeights]);

  return (
    <div className="flex items-end gap-[2px]">
      {heights.map((h, i) => (
        <motion.div
          key={i}
          animate={{ height: h }}
          transition={{ duration: 0.1, ease: "easeOut" }}
          className="flex-1 rounded-full"
          style={{
            background: `linear-gradient(to top, ${color}88, ${color})`,
            minHeight: 2,
          }}
        />
      ))}
    </div>
  );
}