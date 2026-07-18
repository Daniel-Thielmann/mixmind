"use client";

import { useState, useCallback, useMemo, useRef, useEffect } from "react";
import type { Marker, DemoMetadata } from "@/types/video";

interface UseMarkersOptions {
  currentTime: number;
  metadata?: DemoMetadata;
  onMarkerReached?: (marker: Marker) => void;
}

export function useMarkers({
  currentTime,
  metadata,
  onMarkerReached,
}: UseMarkersOptions) {
  const [reachedMarkerIds, setReachedMarkerIds] = useState<Set<number>>(new Set());
  const reachedRef = useRef<Set<number>>(new Set());
  const onMarkerReachedRef = useRef(onMarkerReached);

  useEffect(() => {
    onMarkerReachedRef.current = onMarkerReached;
  }, [onMarkerReached]);

  const markers = useMemo(() => metadata?.markers ?? [], [metadata]);

  const reachedMarkers = useMemo(() => {
    return markers.filter((_, i) => reachedMarkerIds.has(i));
  }, [markers, reachedMarkerIds]);

  const nextMarker = useMemo(() => {
    return markers.find((m) => m.time > currentTime) ?? null;
  }, [markers, currentTime]);

  const prevMarker = useMemo(() => {
    const passed = markers.filter((m) => m.time <= currentTime);
    return passed[passed.length - 1] ?? null;
  }, [markers, currentTime]);

  useEffect(() => {
    for (let i = 0; i < markers.length; i++) {
      const marker = markers[i];
      if (!marker) continue;
      const tolerance = 0.5;
      if (
        currentTime >= marker.time - tolerance &&
        currentTime <= marker.time + tolerance &&
        !reachedRef.current.has(i)
      ) {
        reachedRef.current = new Set([...reachedRef.current, i]);
        setReachedMarkerIds(reachedRef.current);
        onMarkerReachedRef.current?.(marker);
      }
    }
  }, [currentTime, markers]);

  const isMarkerReached = useCallback(
    (index: number) => reachedMarkerIds.has(index),
    [reachedMarkerIds],
  );

  const isNearMarker = useCallback(
    (marker: Marker, threshold = 2) => {
      return Math.abs(currentTime - marker.time) <= threshold;
    },
    [currentTime],
  );

  const resetMarkers = useCallback(() => {
    reachedRef.current = new Set();
    setReachedMarkerIds(new Set());
  }, []);

  return {
    markers,
    reachedMarkers,
    nextMarker,
    prevMarker,
    isMarkerReached,
    isNearMarker,
    resetMarkers,
  };
}
