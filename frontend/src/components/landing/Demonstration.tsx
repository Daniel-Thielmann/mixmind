"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { TrackUploadCard } from "./demo/TrackUploadCard";
import { ProcessingPipeline } from "./demo/ProcessingPipeline";
import { TransitionPreviewPlayer } from "./demo/TransitionPreviewPlayer";
import { FeatureBadge } from "./demo/FeatureBadge";
import { MixMindVideoPlayer } from "@/components/video";
import { AIAnalysisPanel } from "@/components/ai-analysis/AIAnalysisPanel";
import { DEMO_METADATA } from "@/constants/video";
import type { VideoState } from "@/types/video";

type DemoState = "idle" | "processing" | "complete";

const TRACKS = {
  a: {
    label: "Track A",
    title: "Love Me Again (Again) (Wh0 Remix)",
    artist: "John Newman",
    bpm: 124,
    camelot: "8A",
    duration: "3:45",
    accentColor: "#44f3d0",
    audioSrc: "/demo/track_a.mp3",
  },
  b: {
    label: "Track B",
    title: "You Don't Know Me (Radio Edit)",
    artist: "Armand van Helden ft. Duane Harden",
    bpm: 126,
    camelot: "8B",
    duration: "3:52",
    accentColor: "#3b82f6",
    audioSrc: "/demo/track_b.mp3",
  },
};

export function Demonstration() {
  const [demoState, setDemoState] = useState<DemoState>("idle");
  const [videoPlaying, setVideoPlaying] = useState(false);
  const [videoTime, setVideoTime] = useState(0);

  const handleGenerate = useCallback(() => setDemoState("processing"), []);
  const handleProcessingComplete = useCallback(
    () => setDemoState("complete"),
    [],
  );
  const handleReset = useCallback(() => setDemoState("idle"), []);
  const handleVideoState = useCallback(
    (s: VideoState) => setVideoPlaying(s === "playing"),
    [],
  );
  const handleVideoTime = useCallback((t: number) => setVideoTime(t), []);

  return (
    <SectionWrapper id="demo" className="py-24 md:py-32">
      <div className="mx-auto max-w-5xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-16 text-center"
        >
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            Demonstration
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            Upload. Analyze.{" "}
            <span className="bg-linear-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Preview.
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            Drop two tracks and let MixMind&apos;s AI generate a seamless
            transition — before you ever touch the decks.
          </p>
        </motion.div>

        <AnimatePresence mode="wait">
          {demoState === "idle" && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
              className="space-y-8"
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <TrackUploadCard {...TRACKS.a} />
                <TrackUploadCard {...TRACKS.b} />
              </div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-center"
              >
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleGenerate}
                  className="inline-flex h-12 items-center gap-2 rounded-xl bg-primary px-6 text-sm font-semibold text-background shadow-lg shadow-primary/20 transition-all duration-300 hover:bg-primary-dark hover:shadow-xl hover:shadow-primary/30"
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                  </svg>
                  Generate Transition Preview
                </motion.button>
              </motion.div>
            </motion.div>
          )}

          {demoState === "processing" && (
            <ProcessingPipeline
              key="processing"
              onComplete={handleProcessingComplete}
            />
          )}

          {demoState === "complete" && (
            <motion.div
              key="complete"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <TrackUploadCard {...TRACKS.a} compact />
                <TrackUploadCard {...TRACKS.b} compact />
              </div>

              <TransitionPreviewPlayer
                title="AI Generated Transition"
                artist="MixMind AI · Claptone-Inspired Blend"
                bpmA={TRACKS.a.bpm}
                bpmB={TRACKS.b.bpm}
                camelotA={TRACKS.a.camelot}
                camelotB={TRACKS.b.camelot}
                compatibility={98}
                generatedTime="Generated in 3.2s"
                color="#44f3d0"
                audioSrc="/demo/transition.mp3"
              />

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="mx-auto max-w-2xl text-center text-sm leading-relaxed text-text-secondary"
              >
                The AI combined both tracks using harmonic compatibility, phrase
                alignment and energy analysis to generate a seamless transition
                preview before your live performance.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="flex justify-center"
              >
                <FeatureBadge />
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="text-center"
              ></motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Divider */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mx-auto mt-24 mb-16 max-w-4xl"
        >
          <div className="relative flex items-center gap-4">
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border/50 to-transparent" />
            <span className="shrink-0 text-[10px] font-semibold uppercase tracking-[0.3em] text-text-tertiary">
              Watch a real transition analyzed by MixMind
            </span>
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border/50 to-transparent" />
          </div>
        </motion.div>

        {/* Video analysis section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mx-auto max-w-4xl"
        >
          <div suppressHydrationWarning>
            <MixMindVideoPlayer
              src={DEMO_METADATA.src}
              poster={DEMO_METADATA.poster}
              metadata={DEMO_METADATA}
              onStateChange={handleVideoState}
              onTimeUpdate={handleVideoTime}
            />
          </div>

          <div className="mt-8">
            <AIAnalysisPanel currentTime={videoTime} isPlaying={videoPlaying} />
          </div>
        </motion.div>
      </div>
    </SectionWrapper>
  );
}
