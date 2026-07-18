"use client";

import { useState, useCallback, useId, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useYouTubePlayer } from "@/hooks/useYouTubePlayer";
import { useTimeBoundary } from "@/hooks/useTimeBoundary";
import type { VideoPlayerProps, VideoPlayerStatus } from "@/types/video";

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function getYouTubeThumbnail(videoId: string): string {
  return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
}

export function VideoPlayer({
  videoId,
  startTime,
  endTime,
  autoplay = false,
  muted = false,
  loop = false,
  controls = true,
  poster,
  className = "",
  onPlayStateChange,
  onTimeUpdate,
}: VideoPlayerProps) {
  const [status, setStatus] = useState<VideoPlayerStatus>("idle");
  const endedRef = useRef(0);
  const uniqueId = useId();
  const containerId = `yt-player-${uniqueId.replace(/[^a-zA-Z0-9-]/g, "")}`;

  const handlePlayerStateChange = useCallback(
    (event: { data: number }) => {
      if (endedRef.current > 0) {
        endedRef.current--;
        return;
      }

      const YT = window.YT;
      if (!YT) return;

      if (event.data === YT.PlayerState.PLAYING) {
        setStatus("playing");
        onPlayStateChange?.(true);
      } else if (
        event.data === YT.PlayerState.PAUSED ||
        event.data === YT.PlayerState.ENDED
      ) {
        setStatus("paused");
        onPlayStateChange?.(false);
      }
    },
    [onPlayStateChange],
  );

  const handlePlayerError = useCallback(() => {
    setStatus("error");
    onPlayStateChange?.(false);
  }, [onPlayStateChange]);

  const handleBoundaryReached = useCallback(() => {
    endedRef.current = 2;
    setStatus(loop ? "idle" : "ended");
    onPlayStateChange?.(false);
  }, [loop, onPlayStateChange]);

  const { init, play, pause, seekTo, getCurrentTime, playerRef } =
    useYouTubePlayer({
      videoId,
      startTime,
      endTime,
      autoplay,
      muted,
      controls,
      onStateChange: handlePlayerStateChange,
      onError: handlePlayerError,
    });

  const { start: startBoundaryCheck } = useTimeBoundary({
    startTime,
    endTime,
    loop,
    getCurrentTime,
    seekTo,
    pause,
    onBoundaryReached: handleBoundaryReached,
  });

  const handlePlay = useCallback(() => {
    if (!playerRef.current) {
      init(containerId);
    }
    play();
    startBoundaryCheck();
  }, [init, play, startBoundaryCheck, containerId]);

  useEffect(() => {
    if (status !== "playing") return;

    const interval = setInterval(() => {
      const t = getCurrentTime();
      if (t !== undefined) {
        onTimeUpdate?.(t - startTime);
      }
    }, 200);

    return () => clearInterval(interval);
  }, [status, getCurrentTime, onTimeUpdate, startTime]);

  const shouldShowOverlay = status === "idle" || status === "ended";
  const shouldShowLoading = status === "loading";
  const shouldShowError = status === "error";
  const thumbnailUrl = poster || getYouTubeThumbnail(videoId);
  const timeLabel = `${formatTime(startTime)} — ${formatTime(endTime)}`;

  return (
    <div
      className={`group relative overflow-hidden rounded-2xl border border-border bg-card shadow-xl transition-all duration-500 hover:border-primary/20 ${className}`}
      role="region"
      aria-label={`Video player: ${timeLabel}`}
    >
      <div className="absolute inset-0 bg-linear-to-br from-primary/5 via-transparent to-accent-blue/5 opacity-0 transition-opacity duration-500 group-hover:opacity-100 pointer-events-none" />

      <div className="relative">
        <div className="flex items-center justify-between border-b border-border/50 px-5 py-3">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-danger/20">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="#ff5b6e"
                aria-hidden="true"
              >
                <polygon points="9.75,15.02 15.5,11.75 9.75,8.48" />
                <path d="M23.5,6.5c0,0-0.23-1.62-0.94-2.33c-0.9-0.94-1.91-0.95-2.37-1C17.93,2.97,12,3,12,3 s-5.93-0.03-8.19,0.17c-0.46,0.05-1.47,0.06-2.37,1C0.73,4.88,0.5,6.5,0.5,6.5S0.27,8.12,0.5,9.33c0.23,1.22,0.7,2.95,1.46,3.68 c0.71,0.72,1.64,0.7,2.06,0.77c1.5,0.14,6.48,0.18,6.48,0.18s5.93,0.03,8.19-0.17c0.46-0.05,1.47-0.06,2.37-1 c0.71-0.72,0.94-2.33,0.94-2.33S23.73,8.12,23.5,6.5z" />
              </svg>
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
              Real Transition
            </span>
          </div>
          <span className="rounded-full bg-danger/10 px-2 py-0.5 text-[12px] font-medium text-text-secondary">
            Dawn Patrol: Antdot B2B Maz - Afrohouse Set
          </span>
        </div>

        <div className="relative aspect-video w-full bg-background">
          <div id={containerId} className="absolute inset-0 h-full w-full" />

          <AnimatePresence>
            {shouldShowOverlay && (
              <motion.div
                key="overlay"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="absolute inset-0 z-10 flex cursor-pointer items-center justify-center"
                onClick={handlePlay}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    handlePlay();
                  }
                }}
                role="button"
                tabIndex={0}
                aria-label={`Play video from ${timeLabel}`}
              >
                <img
                  src={thumbnailUrl}
                  alt=""
                  className="absolute inset-0 h-full w-full object-cover"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-linear-to-t from-background/80 via-background/20 to-transparent" />
                <div className="absolute inset-0 bg-background/10 backdrop-blur-[1px]" />

                <motion.div
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative z-20 flex h-16 w-16 items-center justify-center rounded-full bg-primary shadow-2xl shadow-primary/40 transition-all duration-300 hover:shadow-primary/60"
                >
                  <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="#090b10"
                    className="ml-1"
                    aria-hidden="true"
                  >
                    <polygon points="5,3 19,12 5,21" />
                  </svg>
                </motion.div>

                <div className="absolute bottom-3 left-3 z-20">
                  <span className="rounded-md bg-background/80 px-2 py-1 text-[10px] font-medium text-text backdrop-blur-sm">
                    {timeLabel}
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {shouldShowLoading && (
            <div className="absolute inset-0 z-20 flex items-center justify-center bg-background">
              <div className="flex items-center gap-2 text-xs text-text-tertiary">
                <div
                  className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"
                  role="status"
                />
                Loading player...
              </div>
            </div>
          )}

          {shouldShowError && (
            <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-background p-6 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-danger/10">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#ff5b6e"
                  strokeWidth="2"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <p className="text-sm font-medium text-text-secondary">
                Video unavailable
              </p>
              <p className="text-xs text-text-tertiary">
                The video could not be loaded. Please try again later.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
