"use client";

import {
  useRef,
  useState,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
} from "react";
import type { VideoState, PlayerAPI } from "@/types/video";

interface UseVideoPlayerOptions {
  src: string;
  poster?: string;
  initialVolume?: number;
  initialMuted?: boolean;
  initialPlaybackRate?: number;
  onPlay?: () => void;
  onPause?: () => void;
  onEnded?: () => void;
  onTimeUpdate?: (time: number) => void;
  onSeek?: (time: number) => void;
  onStateChange?: (state: VideoState) => void;
  playerRef?: React.Ref<PlayerAPI>;
}

export function useVideoPlayer({
  initialVolume = 0.7,
  initialMuted = false,
  initialPlaybackRate = 1,
  onPlay,
  onPause,
  onEnded,
  onTimeUpdate,
  onSeek,
  onStateChange,
  playerRef: externalRef,
}: UseVideoPlayerOptions) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);
  const callbacksRef = useRef({ onPlay, onPause, onEnded, onTimeUpdate, onSeek, onStateChange });

  useEffect(() => {
    callbacksRef.current = { onPlay, onPause, onEnded, onTimeUpdate, onSeek, onStateChange };
  }, [onPlay, onPause, onEnded, onTimeUpdate, onSeek, onStateChange]);

  const [state, setState] = useState<VideoState>("idle");
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolumeState] = useState(initialVolume);
  const [isMuted, setIsMuted] = useState(initialMuted);
  const [playbackRate, setPlaybackRateState] = useState(initialPlaybackRate);
  const [buffered, setBuffered] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isPlaying = state === "playing";
  const isEnded = state === "ended";
  const isLoading = state === "loading";
  const isIdle = state === "idle";

  const updateState = useCallback((newState: VideoState) => {
    setState(newState);
    callbacksRef.current.onStateChange?.(newState);
  }, []);

  const stopRAF = useCallback(() => {
    cancelAnimationFrame(rafRef.current);
  }, []);

  const handleTimeSync = useCallback(function syncTime() {
    const video = videoRef.current;
    if (!video) return;
    const t = video.currentTime;
    if (Math.abs(t - lastTimeRef.current) > 0.01) {
      setCurrentTime(t);
      callbacksRef.current.onTimeUpdate?.(t);
      lastTimeRef.current = t;
    }
    if (!video.paused && !video.ended) {
      rafRef.current = requestAnimationFrame(syncTime);
    }
  }, []);

  const startRAF = useCallback(() => {
    stopRAF();
    rafRef.current = requestAnimationFrame(handleTimeSync);
  }, [handleTimeSync, stopRAF]);

  const seek = useCallback((time: number) => {
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = time;
    setCurrentTime(time);
    callbacksRef.current.onSeek?.(time);
  }, []);

  const play = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.play().then(() => {
      updateState("playing");
      callbacksRef.current.onPlay?.();
      startRAF();
    }).catch((err: DOMException) => {
      if (err.name !== "AbortError") {
        setError(err.message);
        updateState("error");
      }
    });
  }, [updateState, startRAF]);

  const pause = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.pause();
    updateState("paused");
    callbacksRef.current.onPause?.();
    stopRAF();
    setCurrentTime(video.currentTime);
  }, [updateState, stopRAF]);

  const toggle = useCallback(() => {
    if (isEnded) {
      seek(0);
      play();
      return;
    }
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }, [isEnded, isPlaying, seek, play, pause]);

  const setVolume = useCallback((v: number) => {
    const video = videoRef.current;
    if (!video) return;
    const clamped = Math.min(Math.max(v, 0), 1);
    video.volume = clamped;
    setVolumeState(clamped);
    if (clamped > 0 && video.muted) {
      video.muted = false;
      setIsMuted(false);
    }
  }, []);

  const toggleMute = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.muted = !video.muted;
    setIsMuted(video.muted);
  }, []);

  const toggleFullscreen = useCallback(async () => {
    const container = containerRef.current;
    if (!container) return;
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
        setIsFullscreen(false);
      } else {
        await container.requestFullscreen();
        setIsFullscreen(true);
      }
    } catch {
      setIsFullscreen(!!document.fullscreenElement);
    }
  }, []);

  const togglePiP = useCallback(async () => {
    const video = videoRef.current;
    if (!video) return;
    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
      } else {
        await video.requestPictureInPicture();
      }
    } catch {
      // PiP not supported
    }
  }, []);

  const setPlaybackRate = useCallback((rate: number) => {
    const video = videoRef.current;
    if (!video) return;
    video.playbackRate = rate;
    setPlaybackRateState(rate);
  }, []);

  const getCurrentTime = useCallback(() => {
    return videoRef.current?.currentTime ?? 0;
  }, []);

  const getDuration = useCallback(() => {
    return videoRef.current?.duration ?? 0;
  }, []);

  const api = useMemo<PlayerAPI>(
    () => ({
      play, pause, toggle, seek, setVolume, toggleMute,
      toggleFullscreen, togglePiP, setPlaybackRate,
      getCurrentTime, getDuration,
    }),
    [play, pause, toggle, seek, setVolume, toggleMute,
     toggleFullscreen, togglePiP, setPlaybackRate,
     getCurrentTime, getDuration],
  );

  useImperativeHandle(externalRef, () => api, [api]);

  // --- Video event listeners ---
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const onLoadedMetadata = () => {
      setDuration(video.duration);
      setVolumeState(video.volume);
      setIsMuted(video.muted);
      updateState("ready");
    };

    const onPlayEvent = () => {
      updateState("playing");
      startRAF();
    };

    const onPauseEvent = () => {
      if (!video.ended) {
        updateState("paused");
        stopRAF();
        setCurrentTime(video.currentTime);
      }
    };

    const onEndedEvent = () => {
      updateState("ended");
      stopRAF();
      setCurrentTime(video.duration);
      callbacksRef.current.onEnded?.();
    };

    const onWaiting = () => updateState("loading");
    const onCanPlay = () => {
      if (video.paused) {
        updateState("paused");
      } else if (!video.paused) {
        updateState("playing");
      }
    };

    const onProgress = () => {
      if (video.buffered.length > 0) {
        const end = video.buffered.end(video.buffered.length - 1);
        setBuffered(end / (video.duration || 1));
      }
    };

    const onErrorEvent = () => {
      const message = video.error
        ? `Video error (${video.error.code}): ${video.error.message}`
        : "Unknown video error";
      setError(message);
      updateState("error");
    };

    video.addEventListener("loadedmetadata", onLoadedMetadata);
    video.addEventListener("play", onPlayEvent);
    video.addEventListener("pause", onPauseEvent);
    video.addEventListener("ended", onEndedEvent);
    video.addEventListener("waiting", onWaiting);
    video.addEventListener("canplay", onCanPlay);
    video.addEventListener("progress", onProgress);
    video.addEventListener("error", onErrorEvent);

    return () => {
      video.removeEventListener("loadedmetadata", onLoadedMetadata);
      video.removeEventListener("play", onPlayEvent);
      video.removeEventListener("pause", onPauseEvent);
      video.removeEventListener("ended", onEndedEvent);
      video.removeEventListener("waiting", onWaiting);
      video.removeEventListener("canplay", onCanPlay);
      video.removeEventListener("progress", onProgress);
      video.removeEventListener("error", onErrorEvent);
      stopRAF();
    };
  }, [updateState, startRAF, stopRAF]);

  // --- Fullscreen change listener ---
  useEffect(() => {
    const onFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", onFullscreenChange);
    return () =>
      document.removeEventListener("fullscreenchange", onFullscreenChange);
  }, []);

  // --- Keyboard shortcuts ---
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;

      switch (e.code) {
        case "Space":
          e.preventDefault();
          toggle();
          break;
        case "KeyM":
          toggleMute();
          break;
        case "KeyF":
          toggleFullscreen();
          break;
        case "ArrowRight":
          seek(Math.min(getCurrentTime() + 5, getDuration()));
          break;
        case "ArrowLeft":
          seek(Math.max(getCurrentTime() - 5, 0));
          break;
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [toggle, toggleMute, toggleFullscreen, seek, getCurrentTime, getDuration]);

  return {
    videoRef, containerRef,
    state, currentTime, duration, volume, isMuted, playbackRate,
    buffered, isFullscreen, isPlaying, isEnded, isLoading, isIdle, error,
    setVolume, play, pause, toggle, seek, toggleMute,
    toggleFullscreen, togglePiP, setPlaybackRate, api,
  };
}
