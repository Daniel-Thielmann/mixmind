"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { motion } from "framer-motion";

interface TransitionVisualizerProps {
  playing: boolean;
  currentTime: number;
}

const TRACK_1 = {
  name: "Samba",
  artist: "VXSION & Luch-E",
  color: "#44f3d0",
};
const TRACK_2 = {
  name: "Povoada (Remix)",
  artist: "Maz (BR), Antdot & Sued Nunes",
  color: "#8b5cf6",
};

const MARKERS: { time: number; label: string; type: "start" | "blend" | "peak" | "end"; desc?: string }[] = [
  { time: 0, label: "5:10:00", type: "start" },
  { time: 60, label: "5:11:00", type: "blend", desc: "Blend starts" },
  { time: 83, label: "5:11:23", type: "peak", desc: "Peak blend" },
  { time: 164, label: "5:12:44", type: "end" },
];

const DURATION = 164;

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function TransitionVisualizer({ playing, currentTime }: TransitionVisualizerProps) {
  const progress = Math.min(currentTime / DURATION, 1);
  const phase = currentTime < 60 ? "track1" : currentTime < 164 ? "blending" : "track2";

  const barHeights = useMemo(
    () => Array.from({ length: 40 }, (_, i) => ((i * 13 + 7) % 28) + 4),
    []
  );

  const [animatedHeights, setAnimatedHeights] = useState(barHeights);
  const animRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (playing) {
      animRef.current = setInterval(() => {
        setAnimatedHeights(
          Array.from({ length: 40 }, (_, i) => {
            const base = barHeights[i];
            const intensity = currentTime > 60 && currentTime < 120 ? 2.0 : 1.0;
            return Math.min(base + Math.random() * 24 * intensity, 48);
          })
        );
      }, 120);
    }
    return () => {
      if (animRef.current) {
        clearInterval(animRef.current);
        animRef.current = null;
      }
    };
  }, [playing, currentTime, barHeights]);

  useEffect(() => {
    if (!playing) {
      const id = requestAnimationFrame(() => setAnimatedHeights(barHeights));
      return () => cancelAnimationFrame(id);
    }
  }, [playing, barHeights]);

  return (
    <div className="rounded-2xl border border-border bg-card p-5 transition-all duration-500 hover:border-border-light">
      {/* Track labels */}
      <div className="mb-5 flex items-center justify-between">
        <motion.div
          animate={{ opacity: phase === "track1" ? 1 : 0.5 }}
          className="flex-1 text-left"
        >
          <p className="text-xs font-medium text-text">Track 1</p>
          <p className="text-sm font-semibold" style={{ color: TRACK_1.color }}>
            {TRACK_1.name}
          </p>
          <p className="text-[10px] text-text-tertiary">{TRACK_1.artist}</p>
        </motion.div>

        <div className="flex flex-col items-center px-4">
          <motion.div
            animate={{
              scale: phase === "blending" ? [1, 1.15, 1] : 1,
              color: phase === "blending" ? "#44f3d0" : "#6b7a8f",
            }}
            transition={{ duration: 1.5, repeat: phase === "blending" ? Infinity : 0 }}
            className="text-lg"
          >
            ⚡
          </motion.div>
          <span className="text-[10px] text-text-tertiary">Transition</span>
        </div>

        <motion.div
          animate={{ opacity: phase === "track2" ? 1 : 0.5 }}
          className="flex-1 text-right"
        >
          <p className="text-xs font-medium text-text">Track 2</p>
          <p className="text-sm font-semibold" style={{ color: TRACK_2.color }}>
            {TRACK_2.name}
          </p>
          <p className="text-[10px] text-text-tertiary">{TRACK_2.artist}</p>
        </motion.div>
      </div>

      {/* Timeline */}
      <div className="relative mb-4">
        <div className="relative h-2 overflow-hidden rounded-full bg-zinc-800">
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{
              background: phase === "track1"
                ? TRACK_1.color
                : phase === "blending"
                  ? `linear-gradient(90deg, ${TRACK_1.color}, ${TRACK_2.color})`
                  : TRACK_2.color,
            }}
            animate={{ width: `${progress * 100}%` }}
            transition={{ duration: 0.1, ease: "linear" }}
          />
        </div>

        {/* Markers */}
        {MARKERS.filter((m) => m.type !== "start" && m.type !== "end").map((marker) => {
          const pos = (marker.time / DURATION) * 100;
          const isAuge = marker.type === "peak";
          return (
            <div
              key={marker.time}
              className="absolute top-0 flex flex-col items-center"
              style={{ left: `${pos}%`, transform: "translateX(-50%)" }}
            >
              <motion.div
                animate={
                  isAuge && phase === "blending"
                    ? { scale: [1, 1.5, 1], opacity: [0.6, 1, 0.6] }
                    : { scale: 1, opacity: 0.6 }
                }
                transition={{ duration: 1.5, repeat: isAuge && phase === "blending" ? Infinity : 0 }}
                className={`-mt-1 h-3 w-3 rounded-full border-2 border-background ${
                  isAuge ? "bg-primary shadow-lg shadow-primary/40" : "bg-text-tertiary"
                }`}
              />
              <span className="mt-2 text-[9px] font-medium text-text-tertiary whitespace-nowrap">
                {marker.label}
              </span>
              {isAuge && (
                <span className="text-[8px] text-primary whitespace-nowrap">⬆ auge</span>
              )}
            </div>
          );
        })}

        {/* Playhead */}
        <motion.div
          className="absolute top-0 z-10 flex flex-col items-center"
          style={{ left: `${progress * 100}%`, transform: "translateX(-50%)" }}
        >
          <div className="-mt-0.5 h-3 w-0.5 rounded-full bg-text shadow-lg" />
          <div className="mt-0.5 h-1.5 w-1.5 rounded-full bg-text shadow-lg" />
        </motion.div>
      </div>

      {/* Time display */}
      <div className="mb-4 flex items-center justify-between text-[10px] text-text-tertiary">
        <span>{formatTime(Math.max(0, currentTime))}</span>
        <span className="text-[9px] uppercase tracking-wider">
          {phase === "track1" ? "🎵 Track 1" : phase === "blending" ? "⚡ Blending" : "🎵 Track 2"}
        </span>
        <span>{formatTime(DURATION)}</span>
      </div>

      {/* Waveform */}
      <div className="flex h-14 items-end gap-[2px]">
        {animatedHeights.map((h, i) => {
          const t = i / animatedHeights.length;
          const barColor = phase === "track1"
            ? TRACK_1.color
            : phase === "blending"
              ? t < 0.5
                ? TRACK_1.color
                : TRACK_2.color
              : TRACK_2.color;
          return (
            <motion.div
              key={i}
              animate={{ height: h, opacity: playing ? 1 : 0.4 }}
              transition={{ duration: 0.12, ease: "easeOut" }}
              className="flex-1 rounded-full"
              style={{
                background: `linear-gradient(to top, ${barColor}66, ${barColor})`,
                minHeight: 2,
              }}
            />
          );
        })}
      </div>

      {/* Transition zone info */}
      <motion.div
        animate={{
          opacity: phase === "blending" ? 1 : 0.3,
          backgroundColor: phase === "blending" ? "rgba(68, 243, 208, 0.05)" : "transparent" as string,
        }}
        className="mt-3 flex items-center justify-between rounded-lg border border-border/50 p-2.5"
      >
        <div className="flex items-center gap-2 text-[10px]">
          <span className="font-medium text-text-tertiary">Transition zone:</span>
          <span style={{ color: TRACK_1.color }}>5:10:00</span>
          <span className="text-text-tertiary">→</span>
          <span style={{ color: TRACK_2.color }}>5:12:44</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-primary" />
          <span className="text-[10px] font-medium text-primary">
            {currentTime >= 60 && currentTime < 83
              ? "Blending in..."
              : currentTime >= 83 && currentTime < 120
                ? "Peak harmony"
                : currentTime >= 120
                  ? "Track 2 settling"
                  : "Playing Track 1"}
          </span>
        </div>
      </motion.div>
    </div>
  );
}