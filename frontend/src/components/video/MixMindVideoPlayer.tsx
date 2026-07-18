"use client";

import { useCallback, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useVideoPlayer } from "@/hooks/useVideoPlayer";
import { useTimeline } from "@/hooks/useTimeline";
import { useInsights } from "@/hooks/useInsights";
import { useMarkers } from "@/hooks/useMarkers";
import { formatTime } from "@/utils/format";
import { PLAYBACK_RATES } from "@/constants/video";
import type { MixMindVideoProps, DemoMetadata, AIInsight } from "@/types/video";

function PlayIcon({ className }: { className?: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className={className}>
      <polygon points="5,3 19,12 5,21" />
    </svg>
  );
}

function PauseIcon({ className }: { className?: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className={className}>
      <rect x="6" y="4" width="4" height="16" />
      <rect x="14" y="4" width="4" height="16" />
    </svg>
  );
}

function VolumeIcon({ muted, volume }: { muted: boolean; volume: number }) {
  if (muted || volume === 0) {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
        <line x1="23" y1="9" x2="17" y2="15" />
        <line x1="17" y1="9" x2="23" y2="15" />
      </svg>
    );
  }
  if (volume < 0.5) {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
      </svg>
    );
  }
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
    </svg>
  );
}

function FullscreenIcon({ active }: { active: boolean }) {
  if (active) {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="4 14 10 14 10 20" /><polyline points="20 10 14 10 14 4" />
        <line x1="14" y1="10" x2="21" y2="3" /><line x1="3" y1="21" x2="10" y2="14" />
      </svg>
    );
  }
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="15 3 21 3 21 9" /><polyline points="9 21 3 21 3 15" />
      <line x1="21" y1="3" x2="14" y2="10" /><line x1="3" y1="21" x2="10" y2="14" />
    </svg>
  );
}

function PiPIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="3" width="20" height="14" rx="2" />
      <rect x="11" y="9" width="8" height="6" rx="1" />
    </svg>
  );
}

function SpeedIcon({ rate }: { rate: number }) {
  return (
    <span className="text-[11px] font-semibold tabular-nums">{rate}x</span>
  );
}

function InsightsOverlay({ insight, onClose }: { insight: AIInsight; onClose: () => void }) {
  const typeStyles: Record<string, string> = {
    transition: "border-l-primary",
    "eq-swap": "border-l-accent-blue",
    "bass-transfer": "border-l-accent-purple",
    "phrase-match": "border-l-accent-green",
    "camelot-match": "border-l-primary",
    "energy-shift": "border-l-accent-orange",
    confidence: "border-l-accent-green",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, x: -20 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      exit={{ opacity: 0, y: -10, x: -20 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className={`absolute bottom-16 left-4 z-30 max-w-xs rounded-xl border border-border/60 bg-card/95 p-3 shadow-2xl backdrop-blur-xl border-l-2 ${typeStyles[insight.type] ?? "border-l-primary"}`}
      onClick={onClose}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-primary">
            {insight.title}
          </p>
          <p className="mt-0.5 text-[12px] leading-relaxed text-text-secondary">
            {insight.description}
          </p>
          {insight.confidence !== undefined && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <div className="h-1 w-16 overflow-hidden rounded-full bg-zinc-800">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${insight.confidence}%` }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="h-full rounded-full bg-primary"
                />
              </div>
              <span className="text-[10px] font-medium text-text-tertiary">
                {insight.confidence}% confidence
              </span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

function SeekBar({
  currentTime,
  duration,
  buffered,
  onSeek,
  metadata,
}: {
  currentTime: number;
  duration: number;
  buffered: number;
  onSeek: (time: number) => void;
  metadata?: DemoMetadata;
}) {
  const barRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [hoverTime, setHoverTime] = useState<number | null>(null);
  const [hoverX, setHoverX] = useState(0);

  const progress = duration > 0 ? currentTime / duration : 0;
  const bufferedProgress = buffered;

  const getTimeFromEvent = useCallback(
    (e: React.MouseEvent | MouseEvent) => {
      const bar = barRef.current;
      if (!bar) return 0;
      const rect = bar.getBoundingClientRect();
      const x = Math.min(Math.max(e.clientX - rect.left, 0), rect.width);
      return (x / rect.width) * duration;
    },
    [duration],
  );

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      setIsDragging(true);
      const time = getTimeFromEvent(e);
      onSeek(time);

      const handleMouseMove = (e: MouseEvent) => {
        const t = getTimeFromEvent(e);
        onSeek(t);
      };
      const handleMouseUp = () => {
        setIsDragging(false);
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
      };
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    },
    [getTimeFromEvent, onSeek],
  );

  const handleHover = useCallback(
    (e: React.MouseEvent) => {
      const bar = barRef.current;
      if (!bar) return;
      const rect = bar.getBoundingClientRect();
      const x = Math.min(Math.max(e.clientX - rect.left, 0), rect.width);
      setHoverX(e.clientX - rect.left);
      setHoverTime((x / rect.width) * duration);
    },
    [duration],
  );

  const zones = metadata?.transitionZones ?? [];
  const trackAColor = metadata?.tracks.a.color ?? "#44f3d0";
  const trackBColor = metadata?.tracks.b.color ?? "#8b5cf6";
  const markers = metadata?.markers ?? [];

  return (
    <div className="relative w-full">
      <div
        ref={barRef}
        className="group relative h-1.5 w-full cursor-pointer"
        onMouseDown={handleMouseDown}
        onMouseMove={handleHover}
        onMouseLeave={() => setHoverTime(null)}
      >
        {/* Track background with zones */}
        <div className="absolute inset-0 flex overflow-hidden rounded-full bg-zinc-800">
          {zones.length === 0 ? (
            <div className="h-full w-full rounded-full bg-zinc-700" />
          ) : (
            <>
              {/* Track A segment */}
              {zones[0] && zones[0].startTime > 0 && (
                <div
                  className="h-full"
                  style={{
                    width: `${(zones[0].startTime / duration) * 100}%`,
                    backgroundColor: trackAColor,
                    opacity: 0.3,
                  }}
                />
              )}
              {/* Transition zones */}
              {zones.map((zone, i) => {
                const zoneWidth = ((zone.endTime - zone.startTime) / duration) * 100;
                const zoneLeft = (zone.startTime / duration) * 100;
                return (
                  <div
                    key={i}
                    className="h-full"
                    style={{
                      width: `${zoneWidth}%`,
                      marginLeft: `${zoneLeft - (i === 0 ? 0 : (zones[i - 1]?.endTime ?? 0) / duration * 100)}%`,
                      background: `linear-gradient(90deg, ${trackAColor}66, ${trackBColor}66)`,
                    }}
                  />
                );
              })}
              {/* Track B segment */}
              {zones.length > 0 && (
                <div
                  className="h-full flex-1"
                  style={{
                    backgroundColor: trackBColor,
                    opacity: 0.3,
                  }}
                />
              )}
            </>
          )}
        </div>

        {/* Buffered indicator */}
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-white/10 transition-all duration-200"
          style={{ width: `${bufferedProgress * 100}%` }}
        />

        {/* Progress fill */}
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-primary to-accent-blue transition-all duration-75"
          style={{ width: `${progress * 100}%` }}
        />

        {/* Hover tooltip */}
        {hoverTime !== null && (
          <div
            className="absolute -top-8 z-40 -translate-x-1/2 rounded-md bg-card/90 px-2 py-1 text-[10px] font-medium text-text shadow-lg backdrop-blur-sm"
            style={{ left: hoverX }}
          >
            {formatTime(hoverTime)}
          </div>
        )}

        {/* Marker dots */}
        {markers.map((marker, i) => {
          const pos = (marker.time / duration) * 100;
          return (
            <div
              key={i}
              className="absolute top-1/2 z-10 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-zinc-600"
              style={{
                left: `${pos}%`,
                backgroundColor: marker.type === "peak" ? "#44f3d0" : "#52525b",
              }}
            />
          );
        })}

        {/* Playhead */}
        <div
          className={`absolute top-1/2 z-20 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white shadow-lg shadow-black/30 transition-transform ${isDragging ? "scale-125" : "scale-0 group-hover:scale-100"}`}
          style={{ left: `${progress * 100}%` }}
        />
      </div>
    </div>
  );
}

function TimelineSection({
  metadata,
  currentTime,
  duration,
  progress,
  currentPhase,
  markers,
}: {
  metadata?: DemoMetadata;
  currentTime: number;
  duration: number;
  progress: number;
  currentPhase: "track-a" | "blending" | "track-b";
  markers: { time: number; label: string; type: string }[];
}) {
  const trackA = metadata?.tracks.a;
  const trackB = metadata?.tracks.b;
  const chapters = metadata?.chapters ?? [];

  return (
    <div className="space-y-2">
      {/* Track labels */}
      <div className="flex items-center justify-between px-0.5">
        <motion.div
          animate={{ opacity: currentPhase === "track-a" ? 1 : 0.5 }}
          className="flex items-center gap-2"
        >
          {trackA && (
            <>
              <div className="h-2 w-2 rounded-full" style={{ backgroundColor: trackA.color }} />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
                  Track A
                </p>
                <p className="text-[11px] font-medium text-text" style={{ color: trackA.color }}>
                  {trackA.name}
                </p>
              </div>
            </>
          )}
        </motion.div>

        <motion.div
          animate={{ opacity: currentPhase === "blending" ? 1 : 0.4 }}
          className="flex items-center gap-2"
        >
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-text-tertiary">→</span>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-primary">
              Blend
            </span>
          </div>
        </motion.div>

        <motion.div
          animate={{ opacity: currentPhase === "track-b" ? 1 : 0.5 }}
          className="flex items-center gap-2 text-right"
        >
          {trackB && (
            <>
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
                  Track B
                </p>
                <p className="text-[11px] font-medium text-text" style={{ color: trackB.color }}>
                  {trackB.name}
                </p>
              </div>
              <div className="h-2 w-2 rounded-full" style={{ backgroundColor: trackB.color }} />
            </>
          )}
        </motion.div>
      </div>

      {/* Waveform bars */}
      <div className="flex h-10 items-end gap-[1px]">
        {Array.from({ length: 72 }).map((_, i) => {
          const t = i / 72;
          const height = 0.15 + Math.sin(t * Math.PI * 4 + currentTime * 0.5) * 0.25
            + Math.sin(t * Math.PI * 8 + currentTime * 0.8) * 0.15
            + 0.2 * (1 - Math.abs(t - 0.5) * 2);
          const inZone = metadata?.transitionZones.some(
            (z) => {
              const timeAtBar = t * duration;
              return timeAtBar >= z.startTime && timeAtBar <= z.endTime;
            },
          );
          const trackAColor = trackA?.color ?? "#44f3d0";
          const trackBColor = trackB?.color ?? "#8b5cf6";
          const beforeTransition =
            t < (metadata?.transitionZones[0]?.startTime ?? 0) / duration;
          const barStart = inZone
            ? `${trackAColor}44`
            : `${beforeTransition ? trackAColor : trackBColor}33`;
          const barEnd = inZone
            ? `${trackBColor}44`
            : `${beforeTransition ? trackAColor : trackBColor}77`;

          return (
            <div
              key={i}
              className={`timeline-waveform-bar flex-1 rounded-t-[1px] ${
                currentPhase === "blending" ? "opacity-100" : "opacity-60"
              }`}
              style={{
                "--bar-height": `${Math.max(8, height * 100).toFixed(4)}%`,
                "--bar-start": barStart,
                "--bar-end": barEnd,
              } as CSSProperties}
            />
          );
        })}
      </div>

      {/* Chapter markers */}
      <div className="relative flex items-center justify-between">
        {chapters.slice(0, 6).map((ch, i) => {
          const pos = (ch.time / duration) * 100;
          return (
            <div
              key={i}
              className="flex flex-col items-center"
              style={{ marginLeft: i === 0 ? 0 : undefined }}
            >
              <div
                className={`h-1.5 w-0.5 rounded-full ${
                  currentTime >= ch.time ? "bg-primary" : "bg-zinc-700"
                }`}
              />
              <span
                className={`mt-1 text-[9px] font-medium ${
                  currentTime >= ch.time ? "text-text" : "text-text-tertiary"
                }`}
              >
                {ch.label}
              </span>
            </div>
          );
        })}
        {chapters.length > 6 && (
          <span className="text-[9px] text-text-tertiary">+{chapters.length - 6} more</span>
        )}
      </div>
    </div>
  );
}

export function MixMindVideoPlayer({
  src,
  poster,
  className = "",
  metadata,
  onPlay,
  onPause,
  onEnded,
  onTimeUpdate,
  onSeek,
  onMarkerReached,
  onStateChange,
  playerRef,
}: MixMindVideoProps) {
  const [showControls, setShowControls] = useState(true);
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);
  const hideTimeoutRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const {
    videoRef,
    containerRef,
    currentTime,
    duration,
    volume,
    isMuted,
    playbackRate,
    buffered,
    isFullscreen,
    isPlaying,
    isEnded,
    isLoading,
    isIdle,
    error,
    toggle,
    seek,
    setVolume,
    toggleMute,
    toggleFullscreen,
    togglePiP,
    setPlaybackRate,
  } = useVideoPlayer({
    src,
    poster,
    initialVolume: 0.7,
    initialMuted: false,
    playerRef,
    onPlay,
    onPause,
    onEnded,
    onTimeUpdate,
    onSeek,
    onStateChange,
  });

  const { progress, currentPhase, transitionZones } = useTimeline({
    currentTime,
    duration,
    metadata,
  });

  const { currentInsight } = useInsights({
    currentTime,
    metadata,
  });

  const { markers } = useMarkers({
    currentTime,
    metadata,
    onMarkerReached,
  });

  const [showVolumeSlider, setShowVolumeSlider] = useState(false);

  const handleMouseEnter = useCallback(() => {
    clearTimeout(hideTimeoutRef.current);
    setShowControls(true);
  }, []);

  const handleMouseMove = useCallback(() => {
    clearTimeout(hideTimeoutRef.current);
    setShowControls(true);
    hideTimeoutRef.current = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false);
      }
    }, 2500);
  }, [isPlaying]);

  const handleMouseLeave = useCallback(() => {
    clearTimeout(hideTimeoutRef.current);
    if (isPlaying) {
      setShowControls(false);
    }
  }, [isPlaying]);

  const handlePosterClick = useCallback(() => {
    toggle();
  }, [toggle]);

  const needsPoster = isIdle || isEnded;

  return (
    <div className={`${className}`}>
      <div
        ref={containerRef}
        className="group relative aspect-video w-full overflow-hidden rounded-xl bg-black"
        onMouseEnter={handleMouseEnter}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        suppressHydrationWarning
      >
        {/* Video element */}
        <video
          ref={videoRef}
          src={src}
          poster={poster}
          className="h-full w-full object-contain"
          preload="auto"
          playsInline
          onClick={toggle}
        />

        {/* Error state */}
        {error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/80">
            <div className="rounded-full bg-danger/20 p-3">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <p className="text-sm text-danger">Failed to load video</p>
          </div>
        )}

        {/* Poster / Idle overlay */}
        <AnimatePresence>
          {needsPoster && !error && (
            <motion.div
              key="poster"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-10 flex cursor-pointer items-center justify-center"
              onClick={handlePosterClick}
            >
              {poster && (
                <img
                  src={poster}
                  alt="Video poster"
                  className="absolute inset-0 h-full w-full object-cover"
                />
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
              <div className="absolute inset-0 bg-black/20 backdrop-blur-[1px]" />
              <motion.div
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="relative z-20 flex h-16 w-16 items-center justify-center rounded-full bg-primary shadow-2xl shadow-primary/30"
              >
                {isEnded ? (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="#090b10" className="ml-0">
                    <polygon points="5,3 19,12 5,21" />
                  </svg>
                ) : (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="#090b10" className="ml-0.5">
                    <polygon points="5,3 19,12 5,21" />
                  </svg>
                )}
              </motion.div>
              <div className="absolute bottom-3 left-3 z-20">
                <span className="rounded-md bg-black/60 px-2 py-1 text-[10px] font-medium text-white backdrop-blur-sm">
                  {isEnded ? "Replay" : `0:00 / ${formatTime(duration)}`}
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading spinner */}
        <AnimatePresence>
          {isLoading && !needsPoster && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-10 flex items-center justify-center bg-black/40"
            >
              <div className="flex items-center gap-2 text-xs text-text-tertiary">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                Loading...
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Insights overlay */}
        <AnimatePresence>
          {currentInsight && isPlaying && !needsPoster && (
            <InsightsOverlay
              key={currentInsight.time}
              insight={currentInsight}
              onClose={() => {}}
            />
          )}
        </AnimatePresence>

        {/* Controls bar */}
        <AnimatePresence>
          {showControls && !needsPoster && !error && (
            <motion.div
              key="controls"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-x-0 bottom-0 z-20 bg-gradient-to-t from-black/90 via-black/60 to-transparent px-3 pb-2 pt-8"
            >
              {/* Seek bar */}
              <SeekBar
                currentTime={currentTime}
                duration={duration}
                buffered={buffered}
                onSeek={seek}
                metadata={metadata}
              />

              {/* Control buttons row */}
              <div className="mt-2 flex items-center gap-2">
                {/* Play/Pause */}
                <button
                  onClick={toggle}
                  className="flex h-8 w-8 items-center justify-center rounded-full text-white transition-colors hover:bg-white/10"
                  aria-label={isPlaying ? "Pause" : "Play"}
                >
                  {isPlaying ? <PauseIcon /> : <PlayIcon />}
                </button>

                {/* Time */}
                <span className="min-w-[70px] text-[11px] font-medium tabular-nums text-white/80">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>

                {/* Volume */}
                <div
                  className="relative flex items-center"
                  onMouseEnter={() => setShowVolumeSlider(true)}
                  onMouseLeave={() => setShowVolumeSlider(false)}
                >
                  <button
                    onClick={toggleMute}
                    className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/10 hover:text-white"
                    aria-label={isMuted ? "Unmute" : "Mute"}
                  >
                    <VolumeIcon muted={isMuted} volume={volume} />
                  </button>
                  {showVolumeSlider && (
                    <motion.div
                      initial={{ width: 0, opacity: 0 }}
                      animate={{ width: 64, opacity: 1 }}
                      exit={{ width: 0, opacity: 0 }}
                      transition={{ duration: 0.15 }}
                      className="flex items-center"
                    >
                      <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.05}
                        value={isMuted ? 0 : volume}
                        onChange={(e) => setVolume(Number(e.target.value))}
                        className="h-1 w-16 cursor-pointer appearance-none rounded-full bg-white/20 accent-primary
                          [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:appearance-none
                          [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:shadow"
                        aria-label="Volume"
                      />
                    </motion.div>
                  )}
                </div>

                {/* Spacer */}
                <div className="flex-1" />

                {/* Speed */}
                <div className="relative">
                  <button
                    onClick={() => setShowSpeedMenu(!showSpeedMenu)}
                    className="flex h-8 items-center justify-center rounded-full px-2 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                    aria-label="Playback speed"
                  >
                    <SpeedIcon rate={playbackRate} />
                  </button>
                  <AnimatePresence>
                    {showSpeedMenu && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -5 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -5 }}
                        transition={{ duration: 0.12 }}
                        className="absolute bottom-full right-0 mb-2 min-w-[72px] overflow-hidden rounded-lg border border-border/50 bg-card shadow-xl"
                      >
                        {PLAYBACK_RATES.map((rate) => (
                          <button
                            key={rate}
                            onClick={() => {
                              setPlaybackRate(rate);
                              setShowSpeedMenu(false);
                            }}
                            className={`flex w-full items-center justify-center px-3 py-1.5 text-[11px] transition-colors hover:bg-white/5 ${
                              playbackRate === rate
                                ? "font-semibold text-primary"
                                : "font-medium text-text-tertiary"
                            }`}
                          >
                            {rate}x
                          </button>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* PiP */}
                <button
                  onClick={togglePiP}
                  className="flex h-8 w-8 items-center justify-center rounded-full text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                  aria-label="Picture in Picture"
                >
                  <PiPIcon />
                </button>

                {/* Fullscreen */}
                <button
                  onClick={toggleFullscreen}
                  className="flex h-8 w-8 items-center justify-center rounded-full text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                  aria-label={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
                >
                  <FullscreenIcon active={isFullscreen} />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Timeline section below video */}
      <div className="mt-4 rounded-xl border border-border/50 bg-card px-5 py-4">
        <TimelineSection
          metadata={metadata}
          currentTime={currentTime}
          duration={duration}
          progress={progress}
          currentPhase={currentPhase}
          markers={markers}
        />
      </div>
    </div>
  );
}
