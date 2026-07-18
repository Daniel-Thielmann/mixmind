"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import type { VideoPlayerStatus } from "@/types/video";

interface YouTubePlayerConfig {
  videoId: string;
  startTime: number;
  endTime?: number;
  autoplay?: boolean;
  muted?: boolean;
  controls?: boolean;
  onReady?: () => void;
  onStateChange?: (event: { data: number }) => void;
  onError?: (event: { data: number }) => void;
}

type YTPlayerInstance = InstanceType<typeof window.YT.Player> | null;

const YOUTUBE_API_URL = "https://www.youtube.com/iframe_api";

export function useYouTubePlayer({
  videoId,
  startTime,
  endTime,
  autoplay = false,
  muted = false,
  controls = true,
  onReady,
  onStateChange,
  onError,
}: YouTubePlayerConfig) {
  const [status, setStatus] = useState<VideoPlayerStatus>("idle");
  const playerRef = useRef<YTPlayerInstance>(null);
  const containerIdRef = useRef<string>("");
  const initCalledRef = useRef(false);
  const playQueuedRef = useRef(false);

  const buildPlayerOptions = useCallback(
    (containerId: string) => ({
      height: "100%",
      width: "100%",
      videoId,
      playerVars: {
        start: startTime,
        end: endTime,
        autoplay: 0,
        mute: muted ? 1 : 0,
        controls: controls ? 1 : 0,
        rel: 0,
        modestbranding: 1,
        playsinline: 1,
      },
      events: {
        onReady: (event: { target: YTPlayerInstance }) => {
          playerRef.current = event.target;

          if (playQueuedRef.current) {
            playQueuedRef.current = false;
            event.target?.seekTo(startTime, true);
            event.target?.playVideo();
          }

          setStatus((s) => (s === "loading" ? "paused" : s));
          onReady?.();
        },
        onStateChange: (event: { data: number }) => {
          onStateChange?.(event);
        },
        onError: (event: { data: number }) => {
          setStatus("error");
          onError?.(event);
        },
      },
    }),
    [videoId, startTime, endTime, muted, controls, onReady, onStateChange, onError]
  );

  const createPlayer = useCallback(
    (containerId: string) => {
      if (playerRef.current) return;

      if (!window.YT?.Player) {
        setStatus("error");
        return;
      }

      try {
        new window.YT.Player(containerId, buildPlayerOptions(containerId));
        setStatus("loading");
      } catch {
        setStatus("error");
      }
    },
    [buildPlayerOptions]
  );

  const init = useCallback(
    (containerId: string) => {
      if (initCalledRef.current) return;
      initCalledRef.current = true;
      containerIdRef.current = containerId;

      if (window.YT?.Player) {
        createPlayer(containerId);
        return;
      }

      setStatus("loading");

      window.onYouTubeIframeAPIReady = () => {
        createPlayer(containerId);
      };

      const existingScript = document.querySelector<HTMLScriptElement>(
        `script[src="${YOUTUBE_API_URL}"]`
      );

      if (!existingScript) {
        const tag = document.createElement("script");
        tag.src = YOUTUBE_API_URL;
        tag.onerror = () => {
          setStatus("error");
        };
        document.body.appendChild(tag);
      }
    },
    [createPlayer]
  );

  const play = useCallback(() => {
    if (playerRef.current) {
      playerRef.current.playVideo();
    } else {
      playQueuedRef.current = true;
    }
  }, []);

  const pause = useCallback(() => {
    if (playerRef.current) {
      playerRef.current.pauseVideo();
    }
  }, []);

  const seekTo = useCallback((seconds: number) => {
    if (playerRef.current) {
      playerRef.current.seekTo(seconds, true);
    }
  }, []);

  const getCurrentTime = useCallback((): number | undefined => {
    try {
      return playerRef.current?.getCurrentTime();
    } catch {
      return undefined;
    }
  }, []);

  useEffect(() => {
    return () => {
      try { playerRef.current?.destroy(); } catch {}
      playerRef.current = null;
      initCalledRef.current = false;
      playQueuedRef.current = false;
    };
  }, []);

  return {
    status,
    setStatus,
    init,
    play,
    pause,
    seekTo,
    getCurrentTime,
    playerRef,
    containerIdRef,
  };
}
