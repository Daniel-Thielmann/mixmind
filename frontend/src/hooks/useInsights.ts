"use client";

import { useMemo } from "react";
import type { DemoMetadata } from "@/types/video";

interface UseInsightsOptions {
  currentTime: number;
  metadata?: DemoMetadata;
}

export function useInsights({ currentTime, metadata }: UseInsightsOptions) {
  const insights = useMemo(() => metadata?.insights ?? [], [metadata]);

  const currentInsight = useMemo(() => {
    return insights.find((insight) => {
      const end = insight.time + insight.duration;
      return currentTime >= insight.time && currentTime < end;
    }) ?? null;
  }, [insights, currentTime]);

  const insightHistory = useMemo(
    () => insights.filter((insight) => insight.time <= currentTime),
    [insights, currentTime],
  );

  const nextInsight = useMemo(() => {
    const upcoming = insights
      .filter((insight) => insight.time > currentTime)
      .sort((a, b) => a.time - b.time);
    return upcoming[0] ?? null;
  }, [insights, currentTime]);

  const timeToNextInsight = useMemo(() => {
    if (!nextInsight) return null;
    return Math.max(0, nextInsight.time - currentTime);
  }, [nextInsight, currentTime]);

  return {
    currentInsight,
    insightHistory,
    nextInsight,
    timeToNextInsight,
  };
}
