"use client";

import { motion } from "framer-motion";
import type { UploadAnalysisResponse } from "@/types";

import { AIRecommendationCard } from "@/components/ai/AIRecommendationCard";
import { MixMindScoreCard } from "@/components/ai/MixMindScoreCard";
import { WhyThisScore } from "@/components/ai/WhyThisScore";
import { TransitionTimeline } from "@/components/ai/TransitionTimeline";
import { RadarChartCard } from "@/components/ai/RadarChart";
import { HeatIndicators } from "@/components/ai/HeatIndicators";
import { DJExecutionTimeline } from "@/components/ai/DJExecutionTimeline";
import { CompatibilityCard } from "./compatibility-card";
import { TrackCard } from "./track-card";

interface DashboardProps {
  result: UploadAnalysisResponse;
}

export function Dashboard({ result }: DashboardProps) {
  const waveforms = result.waveforms;
  const spectrograms = result.spectrograms;

  if (!waveforms || !spectrograms) {
    return null;
  }

  const r = result.ai_recommendation;
  const compat = result.compatibility;

  return (
    <motion.section
      className="w-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <div className="mx-auto w-full max-w-[1440px] px-4 md:px-6 lg:px-8">
        <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-6 xl:grid-cols-12">
          <div className="md:col-span-3 xl:col-span-6">
            <MixMindScoreCard recommendation={r} compatibility={compat} />
          </div>
          <div className="md:col-span-3 xl:col-span-6">
            <WhyThisScore compatibility={compat} />
          </div>

          <div className="md:col-span-3 xl:col-span-6">
            <TrackCard
              title="Track A"
              analysis={result.track_a}
              waveform={waveforms.track_a}
              spectrogram={spectrograms.track_a}
            />
          </div>
          <div className="md:col-span-3 xl:col-span-6">
            <TrackCard
              title="Track B"
              analysis={result.track_b}
              waveform={waveforms.track_b}
              spectrogram={spectrograms.track_b}
            />
          </div>

          <div className="md:col-span-3 xl:col-span-6">
            <RadarChartCard recommendation={r} compatibility={compat} />
          </div>
          <div className="md:col-span-3 xl:col-span-6">
            <HeatIndicators recommendation={r} compatibility={compat} />
          </div>

          <div className="md:col-span-6 xl:col-span-12">
            <TransitionTimeline
              transitionType={r.transition_type}
              transitionQuality={r.transition_quality}
              transitionLength={r.recommended_transition_length}
            />
          </div>

          <div className="md:col-span-6 xl:col-span-12">
            <CompatibilityCard compatibility={compat} />
          </div>

          <div className="md:col-span-3 xl:col-span-6">
            <AIRecommendationCard recommendation={r} />
          </div>
          <div className="md:col-span-3 xl:col-span-6">
            <DJExecutionTimeline execution={r.dj_execution} />
          </div>
        </div>
      </div>
    </motion.section>
  );
}
