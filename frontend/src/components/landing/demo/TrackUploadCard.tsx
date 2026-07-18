"use client";

import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface TrackUploadCardProps {
  label: string;
  title: string;
  artist: string;
  bpm: number;
  camelot: string;
  duration: string;
  accentColor: string;
  compact?: boolean;
  audioSrc?: string;
  previewStartSeconds?: number;
  previewEndSeconds?: number;
}

function fmt(t: number) {
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function TrackUploadCard({
  label,
  title,
  artist,
  bpm,
  camelot,
  duration,
  accentColor,
  compact = false,
  audioSrc,
  previewStartSeconds = 0,
  previewEndSeconds,
}: TrackUploadCardProps) {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [segmentStart, setSegmentStart] = useState(0);
  const [mediaError, setMediaError] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const seekRef = useRef<HTMLDivElement | null>(null);

  const togglePlay = useCallback(() => {
    if (mediaError) return;
    setPlaying((p) => !p);
  }, [mediaError]);

  const handleSeek = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current || !seekRef.current) return;
    const rect = seekRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    audioRef.current.currentTime = segmentStart + x * audioDuration;
  }, [audioDuration, segmentStart]);

  useEffect(() => {
    if (!audioSrc) return;
    const el = new Audio(audioSrc);
    el.preload = "metadata";
    el.ontimeupdate = () => {
      const start = Math.min(previewStartSeconds, el.duration);
      const end = Math.min(previewEndSeconds ?? el.duration, el.duration);
      if (el.currentTime >= end) {
        el.pause();
        el.currentTime = start;
        setCurrentTime(0);
        setPlaying(false);
        return;
      }
      setCurrentTime(Math.max(0, el.currentTime - start));
    };
    el.onloadedmetadata = () => {
      const start = Math.min(previewStartSeconds, el.duration);
      const end = Math.max(start, Math.min(previewEndSeconds ?? el.duration, el.duration));
      setMediaError(false);
      setSegmentStart(start);
      setAudioDuration(end - start);
      setCurrentTime(0);
      el.currentTime = start;
    };
    el.onended = () => {
      el.currentTime = Math.min(previewStartSeconds, el.duration);
      setCurrentTime(0);
      setPlaying(false);
    };
    el.onpause = () => setPlaying(false);
    el.onerror = () => { setPlaying(false); setMediaError(true); };
    audioRef.current = el;
    return () => {
      el.pause();
      el.src = "";
    };
  }, [audioSrc, previewEndSeconds, previewStartSeconds]);

  useEffect(() => {
    if (!audioRef.current) return;
    if (playing) {
      void audioRef.current.play().catch(() => {
        setPlaying(false);
        setMediaError(true);
      });
    } else {
      audioRef.current.pause();
    }
  }, [playing]);

  const waveformBars = useMemo(
    () => Array.from({ length: compact ? 30 : 40 }, (_, i) => ((i * 19 + 7) % 22) + 6),
    [compact]
  );

  const progress = audioDuration > 0 ? currentTime / audioDuration : 0;

  return (
    <motion.div layout className="group relative overflow-hidden rounded-2xl border border-border/60 bg-card/50 p-5 backdrop-blur-sm transition-all duration-500 hover:border-border-light">
      <div className="pointer-events-none absolute -inset-1 opacity-0 transition-opacity duration-500 group-hover:opacity-20 blur-xl"
        style={{ background: `radial-gradient(ellipse at center, ${accentColor}, transparent)` }}
      />
      <div className="relative">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-[10px] font-semibold uppercase tracking-[0.2em]" style={{ color: accentColor }}>
            {label}
          </span>
          <span className="text-[10px] text-text-tertiary">{duration}</span>
        </div>
        <h3 className="font-semibold text-text leading-snug text-sm">{title}</h3>
        <p className="mt-0.5 text-xs text-text-tertiary">{artist}</p>

        <div className="mt-3 flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={togglePlay}
            disabled={mediaError || !audioSrc}
            aria-label={mediaError ? `${label} preview unavailable` : `Play ${label} preview`}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-colors"
            style={{ backgroundColor: `${accentColor}20`, color: accentColor }}
          >
            {mediaError ? (
              <span className="text-xs font-bold">!</span>
            ) : playing ? (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="4" width="4" height="16" rx="1" />
                <rect x="14" y="4" width="4" height="16" rx="1" />
              </svg>
            ) : (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5,3 19,12 5,21" />
              </svg>
            )}
          </motion.button>

          <div className="flex flex-1 items-end gap-[1.5px]" style={{ height: compact ? 24 : 32 }}>
            <AnimatePresence mode="popLayout">
              {waveformBars.map((h, i) => {
                const pos = i / waveformBars.length;
                const isPlayed = pos <= progress;
                const animatedH = playing
                  ? Math.min(h + ((i * 11 + 5) % 14), compact ? 24 : 32)
                  : h * 0.35;
                return (
                  <motion.div
                    key={`${i}-${playing}`}
                    animate={{ height: animatedH }}
                    transition={{ duration: playing ? 0.06 : 0.3, ease: "easeOut" }}
                    className="flex-1 rounded-full"
                    style={{
                      background: `linear-gradient(to top, ${accentColor}${isPlayed ? "88" : "22"}, ${accentColor}${isPlayed ? "CC" : "44"})`,
                      minHeight: 2,
                    }}
                  />
                );
              })}
            </AnimatePresence>
          </div>
        </div>

        <div
          ref={seekRef}
          onClick={handleSeek}
          className="group/seeker relative mt-2 h-1.5 cursor-pointer overflow-hidden rounded-full bg-zinc-800"
        >
          <motion.div
            animate={{ width: `${progress * 100}%` }}
            transition={{ duration: 0.1, ease: "linear" }}
            className="absolute inset-y-0 left-0 rounded-full"
            style={{ background: `linear-gradient(90deg, ${accentColor}, ${accentColor}cc)` }}
          />
        </div>

        <div className="mt-1 flex items-center justify-between text-[9px] text-text-tertiary">
          <span>{fmt(currentTime)}</span>
          <span>{fmt(audioDuration)}</span>
        </div>

        <div className="mt-3 flex items-center gap-4 border-t border-border/30 pt-3">
          <div className="flex items-center gap-1.5">
            <span className="text-[9px] font-medium text-text-tertiary">BPM</span>
            <span className="text-xs font-semibold text-text">{bpm}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[9px] font-medium text-text-tertiary">Camelot</span>
            <span className="text-xs font-semibold text-text">{camelot}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
