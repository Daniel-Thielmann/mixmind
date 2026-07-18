"use client";

import { useMemo } from "react";
import { TransitionTimeline } from "./TransitionTimeline";
import { LiveCommentary } from "./LiveCommentary";
import { AIFocus } from "./AIFocus";
import { FinalVerdict } from "./FinalVerdict";
import { MOCK_TRANSITION_ANALYSIS } from "@/mocks/mock-transition-analysis";

interface AIAnalysisPanelProps {
  currentTime: number;
  isPlaying: boolean;
  onReplay?: () => void;
}

export function AIAnalysisPanel({
  currentTime,
  isPlaying,
  onReplay,
}: AIAnalysisPanelProps) {
  const analysis = MOCK_TRANSITION_ANALYSIS;
  const duration = analysis.duration;
  const isEnded = useMemo(() => currentTime >= duration - 0.5, [currentTime, duration]);

  return (
    <div className={`space-y-10 transition-opacity ${isPlaying ? "opacity-100" : "opacity-90"}`}>
      <TransitionTimeline
        analysis={analysis}
        currentTime={currentTime}
        duration={duration}
      />

      <div className="grid gap-8">
        <LiveCommentary
          analysis={analysis}
          currentTime={currentTime}
        />
        <AIFocus
          analysis={analysis}
          currentTime={currentTime}
        />
      </div>

      <FinalVerdict
        analysis={analysis}
        visible={isEnded}
        onReplay={onReplay ?? (() => {})}
      />
    </div>
  );
}
