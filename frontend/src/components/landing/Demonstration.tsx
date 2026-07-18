"use client";

import { useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { TrackUploadCard } from "./demo/TrackUploadCard";
import { ProcessingPipeline } from "./demo/ProcessingPipeline";
import { TransitionPreviewPlayer } from "./demo/TransitionPreviewPlayer";
import { FeatureBadge } from "./demo/FeatureBadge";
import { AIAnalysisPanel } from "@/components/ai-analysis/AIAnalysisPanel";
import { DEMO_METADATA } from "@/constants/video";
import type { VideoState } from "@/types/video";
import { useDemoMedia } from "@/hooks/useDemoMedia";

type DemoState = "idle" | "processing" | "complete";

const MixMindVideoPlayer = dynamic(
  () => import("@/components/video").then((module) => module.MixMindVideoPlayer),
  {
    ssr: false,
    loading: () => (
      <div className="aspect-video w-full animate-pulse rounded-xl bg-black" />
    ),
  },
);

const buildTracks = (trackA: string, trackB: string) => ({
  a: {
    label: "Track A",
    title: "Love Me Again (Again) (Wh0 Remix)",
    artist: "John Newman",
    bpm: 124,
    camelot: "8A",
    duration: "2:10–3:10",
    accentColor: "#44f3d0",
    audioSrc: trackA,
    previewStartSeconds: 130,
    previewEndSeconds: 190,
  },
  b: {
    label: "Track B",
    title: "You Don't Know Me (Radio Edit)",
    artist: "Armand van Helden ft. Duane Harden",
    bpm: 126,
    camelot: "8B",
    duration: "3:52",
    accentColor: "#3b82f6",
    audioSrc: trackB,
  },
});

export function Demonstration() {
  const [demoState, setDemoState] = useState<DemoState>("idle");
  const [videoPlaying, setVideoPlaying] = useState(false);
  const [videoTime, setVideoTime] = useState(0);
  const { targetRef, manifest, loading, error, retry } = useDemoMedia();
  const tracks = buildTracks(
    manifest?.assets.trackB.url ?? "",
    manifest?.assets.trackA.url ?? "",
  );

  const handleGenerate = useCallback(() => setDemoState("processing"), []);
  const handleProcessingComplete = useCallback(
    () => setDemoState("complete"),
    [],
  );
  const handleVideoState = useCallback(
    (s: VideoState) => setVideoPlaying(s === "playing"),
    [],
  );
  const handleVideoTime = useCallback((t: number) => setVideoTime(t), []);

  return (
    <SectionWrapper id="demo" className="py-24 md:py-32">
      <div className="mx-auto max-w-5xl px-6">
        <div ref={targetRef} aria-hidden="true" />
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

        {(loading || error || !manifest) && (
          <div className="mb-12 flex min-h-48 items-center justify-center rounded-2xl border border-border bg-card/50 p-8 text-center">
            {loading ? (
              <p className="animate-pulse text-sm text-text-secondary">Loading real demonstration media…</p>
            ) : error ? (
              <div><p className="text-sm text-text-secondary">{error}</p><button type="button" onClick={() => void retry()} className="mt-4 rounded-lg border border-border px-4 py-2 text-sm text-text">Try again</button></div>
            ) : (
              <p className="text-sm text-text-secondary">The demonstration loads when this section enters view.</p>
            )}
          </div>
        )}

        {manifest && <AnimatePresence mode="wait">
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
                <TrackUploadCard {...tracks.a} />
                <TrackUploadCard {...tracks.b} />
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
                <TrackUploadCard {...tracks.a} compact />
                <TrackUploadCard {...tracks.b} compact />
              </div>

              <TransitionPreviewPlayer
                title="AI Generated Transition"
                artist="MixMind AI · Claptone-Inspired Blend"
                bpmA={tracks.a.bpm}
                bpmB={tracks.b.bpm}
                camelotA={tracks.a.camelot}
                camelotB={tracks.b.camelot}
                compatibility={98}
                generatedTime="Generated in 3.2s"
                color="#44f3d0"
                audioSrc={manifest.assets.transition.url}
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
        </AnimatePresence>}

        {/* Divider */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mx-auto mt-24 mb-16 max-w-4xl"
        >
          <div className="relative flex items-center gap-4">
            <div className="h-px flex-1 bg-linear-to-r from-transparent via-border/50 to-transparent" />
            <span className="shrink-0 text-[10px] font-semibold uppercase tracking-[0.3em] text-text-tertiary">
              Watch a real transition analyzed by MixMind
            </span>
            <div className="h-px flex-1 bg-linear-to-r from-transparent via-border/50 to-transparent" />
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
          {manifest ? <div>
            <MixMindVideoPlayer
              src={manifest.assets.video.url}
              poster={manifest.assets.poster.url}
              metadata={DEMO_METADATA}
              onStateChange={handleVideoState}
              onTimeUpdate={handleVideoTime}
            />
          </div> : <div className="aspect-video w-full rounded-xl border border-border bg-black/70" />}

          <div className="mt-8">
            <AIAnalysisPanel currentTime={videoTime} isPlaying={videoPlaying} />
          </div>
        </motion.div>
      </div>
    </SectionWrapper>
  );
}
