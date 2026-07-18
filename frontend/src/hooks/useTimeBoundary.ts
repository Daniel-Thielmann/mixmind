"use client";

import { useRef, useCallback, useEffect } from "react";

interface TimeBoundaryConfig {
  startTime: number;
  endTime: number;
  loop: boolean;
  getCurrentTime: () => number | undefined;
  seekTo: (seconds: number) => void;
  pause: () => void;
  onBoundaryReached?: () => void;
}

export function useTimeBoundary({
  startTime,
  endTime,
  loop,
  getCurrentTime,
  seekTo,
  pause,
  onBoundaryReached,
}: TimeBoundaryConfig) {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const seekInProgressRef = useRef(false);

  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(() => {
    stop();

    intervalRef.current = setInterval(() => {
      if (seekInProgressRef.current) return;

      const currentTime = getCurrentTime();
      if (currentTime === undefined) return;

      if (currentTime >= endTime) {
        seekInProgressRef.current = true;
        onBoundaryReached?.();
        seekTo(startTime);
        pause();

        if (loop) {
          requestAnimationFrame(() => {
            seekInProgressRef.current = false;
          });
        } else {
          seekInProgressRef.current = false;
        }
      }
    }, 200);
  }, [startTime, endTime, loop, getCurrentTime, seekTo, pause]);

  useEffect(() => {
    return () => stop();
  }, [stop]);

  return { start, stop };
}
