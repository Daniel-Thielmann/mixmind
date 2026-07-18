"use client";

import { useState, useMemo, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";

interface TransitionPreviewPlayerProps {
  title: string;
  artist: string;
  bpmA: number;
  bpmB: number;
  camelotA: string;
  camelotB: string;
  compatibility: number;
  generatedTime: string;
  color: string;
  audioSrc?: string;
}

function fmt(t: number) {
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function TransitionPreviewPlayer({
  title,
  artist,
  bpmA,
  bpmB,
  camelotA,
  camelotB,
  compatibility,
  generatedTime,
  color,
  audioSrc,
}: TransitionPreviewPlayerProps) {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [mediaError, setMediaError] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const seekRef = useRef<HTMLDivElement | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const togglePlay = useCallback(() => {
    if (mediaError) return;
    setPlaying((p) => !p);
  }, [mediaError]);

  const handleSeek = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current || !seekRef.current) return;
    const rect = seekRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    audioRef.current.currentTime = x * audioDuration;
  }, [audioDuration]);

  useEffect(() => {
    if (!audioSrc) return;
    const el = new Audio(audioSrc);
    el.preload = "metadata";
    el.ontimeupdate = () => { setCurrentTime(el.currentTime); };
    el.onloadedmetadata = () => { setMediaError(false); setAudioDuration(el.duration); };
    el.onended = () => { setPlaying(false); };
    el.onpause = () => { setPlaying(false); };
    el.onerror = () => { setPlaying(false); setMediaError(true); };
    audioRef.current = el;
    return () => {
      el.pause();
      el.src = "";
    };
  }, [audioSrc]);

  useEffect(() => {
    if (!audioRef.current || !audioSrc) return;
    if (playing) {
      void audioRef.current.play().catch(() => {
        setPlaying(false);
        setMediaError(true);
      });
    } else {
      audioRef.current.pause();
    }
  }, [playing, audioSrc]);

  const bars = useMemo(
    () =>
      Array.from({ length: 60 }, (_, i) => {
        const pos = i / 60;
        const envelope =
          pos < 0.3 ? pos / 0.3 : pos < 0.7 ? 1 : 1 - (pos - 0.7) / 0.3;
        return (((i * 13 + 5) % 18) + 4) * envelope;
      }),
    []
  );

  const [heights, setHeights] = useState(bars);

  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        setHeights(bars.map((h) => Math.min(h + Math.random() * 14, 36)));
      }, 80);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [playing, bars]);

  useEffect(() => {
    if (!playing) {
      const id = requestAnimationFrame(() => setHeights(bars));
      return () => cancelAnimationFrame(id);
    }
  }, [playing, bars]);

  const idleHeights = bars.map((h) => h * 0.3);
  const displayHeights = playing ? heights : idleHeights;
  const progress = audioDuration > 0 ? currentTime / audioDuration : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
      className="group relative"
    >
      <div
        className="pointer-events-none absolute -inset-6 rounded-3xl opacity-0 transition-opacity duration-700 group-hover:opacity-25 blur-3xl"
        style={{ background: `radial-gradient(ellipse at center, ${color}, transparent)` }}
      />

      <div
        className="relative overflow-hidden rounded-2xl border-2 transition-all duration-500"
        style={{
          borderColor: `${color}25`,
          background: `linear-gradient(135deg, ${color}06, transparent)`,
        }}
      >
        <div
          className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100"
          style={{ background: `linear-gradient(135deg, ${color}10, transparent 60%)` }}
        />

        <div className="relative p-6 md:p-8">
          <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="mb-1 flex items-center gap-2">
                <span
                  className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
                  style={{ backgroundColor: `${color}18`, color }}
                >
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                  </svg>
                  AI Transition Preview
                </span>
                <span className="rounded-full bg-zinc-800/80 px-2 py-0.5 text-[9px] font-medium text-text-tertiary">
                  {generatedTime}
                </span>
              </div>
              <h3 className="mt-2 text-lg font-bold text-text md:text-xl">{title}</h3>
              <p className="text-sm text-text-secondary">{artist}</p>
            </div>

            <div
              className="flex shrink-0 flex-col items-center rounded-xl border px-4 py-2.5"
              style={{ borderColor: `${color}20`, backgroundColor: `${color}08` }}
            >
              <span className="text-[9px] font-medium uppercase tracking-wider text-text-tertiary">Compatibility</span>
              <span className="text-2xl font-bold" style={{ color }}>
                {compatibility}%
              </span>
            </div>
          </div>

          <div className="mb-4 flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.92 }}
              onClick={togglePlay}
              disabled={mediaError || !audioSrc}
              aria-label={mediaError ? "Transition preview unavailable" : "Play transition preview"}
              className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full shadow-lg transition-all duration-300"
              style={{
                backgroundColor: color,
                color: "#090b10",
                boxShadow: `0 0 30px ${color}40`,
              }}
            >
              {mediaError ? (
                <span className="text-lg font-bold">!</span>
              ) : playing ? (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16" rx="1" />
                  <rect x="14" y="4" width="4" height="16" rx="1" />
                </svg>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5,3 19,12 5,21" />
                </svg>
              )}
            </motion.button>

            <div className="flex flex-1 items-end gap-[1.5px]" style={{ height: 56 }}>
              {displayHeights.map((h, i) => {
                const pos = i / displayHeights.length;
                const isPlayed = pos <= progress;
                return (
                  <motion.div
                    key={i}
                    animate={{ height: h }}
                    transition={{ duration: 0.06, ease: "easeOut" }}
                    className="flex-1 rounded-full"
                    style={{
                      background: `linear-gradient(to top, ${color}${isPlayed ? "88" : "22"}, ${color}${isPlayed ? "CC" : "44"})`,
                      minHeight: 2,
                    }}
                  />
                );
              })}
            </div>
          </div>

          <div
            ref={seekRef}
            onClick={handleSeek}
            className="group/seeker relative mb-4 h-2 cursor-pointer overflow-hidden rounded-full bg-zinc-800"
          >
            <motion.div
              animate={{ width: `${progress * 100}%` }}
              transition={{ duration: 0.1, ease: "linear" }}
              className="absolute inset-y-0 left-0 rounded-full"
              style={{ background: `linear-gradient(90deg, ${color}, ${color}cc)` }}
            />
            <motion.div
              animate={{ left: `${progress * 100}%` }}
              transition={{ duration: 0.1, ease: "linear" }}
              className="absolute top-1/2 -mt-1.5 h-3 w-3 -ml-1.5 rounded-full opacity-0 transition-opacity duration-200 group-hover/seeker:opacity-100"
              style={{ backgroundColor: color }}
            />
          </div>

          <div className="-mt-2 mb-4 flex items-center justify-between text-[10px] text-text-tertiary">
            <span>{fmt(currentTime)}</span>
            <span>{fmt(audioDuration)}</span>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MetricBox label="BPM" value={`${bpmA} → ${bpmB}`} highlight={false} />
            <MetricBox label="Camelot" value={`${camelotA} → ${camelotB}`} highlight={false} />
            <MetricBox label="Transition" value="Excellent" highlight={true} color={color} />
            <MetricBox label="AI Confidence" value="96%" highlight={true} color={color} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function MetricBox({
  label,
  value,
  highlight,
  color,
}: {
  label: string;
  value: string;
  highlight: boolean;
  color?: string;
}) {
  return (
    <div className="rounded-lg border border-border/40 bg-card/30 p-2.5 text-center transition-colors duration-300">
      <p className="text-[9px] font-medium uppercase tracking-wider text-text-tertiary">{label}</p>
      <p
        className="mt-0.5 text-xs font-semibold"
        style={{ color: highlight && color ? color : undefined }}
      >
        {value}
      </p>
    </div>
  );
}
