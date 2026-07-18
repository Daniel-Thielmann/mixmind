"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface VideoDemoProps {
  onPlayStateChange: (playing: boolean) => void;
  onTimeUpdate: (relativeTime: number) => void;
}

const VIDEO_ID = "GtSCkHk9fLw";
const START_SEC = 18600;
const END_SEC = 18764;

declare global {
  interface Window {
    YT: {
      Player: new (id: string, opts: YTPlayerOptions) => YTPlayer;
      PlayerState: { PLAYING: number; PAUSED: number; ENDED: number; BUFFERING: number };
    };
    onYouTubeIframeAPIReady: (() => void) | undefined;
  }
}

interface YTPlayer {
  playVideo: () => void;
  pauseVideo: () => void;
  seekTo: (seconds: number, allowSeekAhead: boolean) => void;
  getCurrentTime: () => number;
  destroy: () => void;
}

interface YTPlayerOptions {
  height: string;
  width: string;
  videoId: string;
  playerVars?: Record<string, string | number | undefined>;
  events?: {
    onStateChange?: (event: { data: number }) => void;
    onReady?: () => void;
  };
}

export function VideoDemo({ onPlayStateChange, onTimeUpdate }: VideoDemoProps) {
  const [state, setState] = useState<"idle" | "loading" | "playing" | "ended">("idle");
  const playerRef = useRef<YTPlayer | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const apiReadyRef = useRef(false);

  const stopTimeUpdate = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const startTimeUpdate = useCallback(() => {
    stopTimeUpdate();
    intervalRef.current = setInterval(() => {
      try {
        const t = playerRef.current?.getCurrentTime();
        if (t !== undefined && t !== null) {
          const relative = t - START_SEC;
          if (relative >= 0) {
            onTimeUpdate(relative);
          }
          if (t >= END_SEC) {
            playerRef.current?.pauseVideo();
            playerRef.current?.seekTo(START_SEC, true);
            setState("idle");
            onPlayStateChange(false);
            stopTimeUpdate();
          }
        }
      } catch {
        stopTimeUpdate();
      }
    }, 100);
  }, [onTimeUpdate, onPlayStateChange, stopTimeUpdate]);

  const handleStateChange = useCallback(
    (event: { data: number }) => {
      if (event.data === window.YT.PlayerState.PLAYING) {
        setState("playing");
        onPlayStateChange(true);
        startTimeUpdate();
      } else if (event.data === window.YT.PlayerState.PAUSED || event.data === window.YT.PlayerState.ENDED) {
        setState("idle");
        onPlayStateChange(false);
        stopTimeUpdate();
      }
    },
    [onPlayStateChange, startTimeUpdate, stopTimeUpdate]
  );

  useEffect(() => {
    return () => {
      stopTimeUpdate();
      playerRef.current?.destroy();
    };
  }, [stopTimeUpdate]);

  const createPlayer = useCallback(() => {
    if (!apiReadyRef.current) return;
    if (playerRef.current) return;
    playerRef.current = new window.YT.Player("youtube-player", {
      height: "100%",
      width: "100%",
      videoId: VIDEO_ID,
      playerVars: {
        start: START_SEC,
        end: END_SEC,
        autoplay: 1,
        rel: 0,
        controls: 1,
        modestbranding: 1,
        showinfo: 0,
      },
      events: {
        onStateChange: handleStateChange,
      },
    });
    setState("loading");
  }, [handleStateChange]);

  const handlePlay = useCallback(() => {
    if (playerRef.current) {
      playerRef.current.playVideo();
      setState("loading");
    } else {
      if (!window.YT) {
        const tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        tag.onload = () => {
          apiReadyRef.current = true;
          if (window.YT?.Player) {
            createPlayer();
          }
        };
        document.body.appendChild(tag);
      } else if (window.YT?.Player) {
        apiReadyRef.current = true;
        createPlayer();
      } else {
        window.onYouTubeIframeAPIReady = () => {
          apiReadyRef.current = true;
          createPlayer();
        };
      }
    }
  }, [createPlayer]);

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border bg-card shadow-xl transition-all duration-500 hover:border-primary/20">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent-blue/5 opacity-0 transition-opacity duration-500 group-hover:opacity-100 pointer-events-none" />

      <div className="relative">
        <div className="flex items-center justify-between border-b border-border/50 px-5 py-3">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-danger/20">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="#ff5b6e">
                <polygon points="9.75,15.02 15.5,11.75 9.75,8.48" />
                <path d="M23.5,6.5c0,0-0.23-1.62-0.94-2.33c-0.9-0.94-1.91-0.95-2.37-1C17.93,2.97,12,3,12,3 s-5.93-0.03-8.19,0.17c-0.46,0.05-1.47,0.06-2.37,1C0.73,4.88,0.5,6.5,0.5,6.5S0.27,8.12,0.5,9.33c0.23,1.22,0.7,2.95,1.46,3.68 c0.71,0.72,1.64,0.7,2.06,0.77c1.5,0.14,6.48,0.18,6.48,0.18s5.93,0.03,8.19-0.17c0.46-0.05,1.47-0.06,2.37-1 c0.71-0.72,0.94-2.33,0.94-2.33S23.73,8.12,23.5,6.5z" />
              </svg>
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">
              Real Transition
            </span>
          </div>
          <span className="rounded-full bg-danger/10 px-2 py-0.5 text-[10px] font-medium text-danger">
            YouTube
          </span>
        </div>

        <div ref={containerRef} className="relative aspect-video w-full bg-background">
          <AnimatePresence mode="wait">
            {state === "idle" || state === "ended" ? (
              <motion.div
                key="overlay"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-10 flex cursor-pointer items-center justify-center"
                onClick={handlePlay}
              >
                <img
                  src={`https://img.youtube.com/vi/${VIDEO_ID}/maxresdefault.jpg`}
                  alt="Video thumbnail"
                  className="absolute inset-0 h-full w-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-background/20 to-transparent" />
                <div className="absolute inset-0 bg-background/10 backdrop-blur-[1px]" />

                <motion.div
                  whileHover={{ scale: 1.1 }}
                  className="relative z-20 flex h-16 w-16 items-center justify-center rounded-full bg-primary shadow-2xl shadow-primary/40 transition-all duration-300 hover:shadow-primary/60"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="#090b10" className="ml-1">
                    <polygon points="5,3 19,12 5,21" />
                  </svg>
                </motion.div>

                <div className="absolute bottom-3 left-3 z-20">
                  <span className="rounded-md bg-background/80 px-2 py-1 text-[10px] font-medium text-text backdrop-blur-sm">
                    5:10:00 — 5:12:44
                  </span>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="player"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0"
              >
                <div id="youtube-player" className="h-full w-full" />
                {state === "loading" && (
                  <div className="absolute inset-0 flex items-center justify-center bg-background">
                    <div className="flex items-center gap-2 text-xs text-text-tertiary">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                      Loading player...
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}