"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { AudioPlayer } from "./AudioPlayer";
import { FrequencyBars } from "./FrequencyBars";
import { VideoDemo } from "./VideoDemo";
import { TransitionVisualizer } from "./TransitionVisualizer";

export function Demonstration() {
  const [playing, setPlaying] = useState(false);
  const [videoPlaying, setVideoPlaying] = useState(false);
  const [videoTime, setVideoTime] = useState(0);

  const handlePlayStateChange = useCallback((p: boolean) => {
    setVideoPlaying(p);
  }, []);

  const handleTimeUpdate = useCallback((t: number) => {
    setVideoTime(t);
  }, []);

  return (
    <SectionWrapper id="demo" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
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
            Hear the{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Difference
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            Listen to how MixMind transforms a rough transition into a seamless harmonic blend.
          </p>
        </motion.div>

        <div className="grid gap-8 md:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <AudioPlayer label="Before MixMind" trackTitle="Rough Transition — 124 → 126 BPM" color="text-danger" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="group relative overflow-hidden rounded-2xl border border-primary/20 bg-card p-6 transition-all duration-500 hover:border-primary/40">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100 pointer-events-none" />
              <div className="relative">
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
                    After MixMind
                  </span>
                  <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
                    AI Optimized
                  </span>
                </div>
                <p className="mb-4 text-sm font-medium text-text">Seamless Blend — 124 → 126 BPM</p>

                <div className="mb-4 flex items-center gap-3">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setPlaying(!playing)}
                    className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-background shadow-lg shadow-primary/20"
                  >
                    {playing ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <rect x="6" y="4" width="4" height="16" />
                        <rect x="14" y="4" width="4" height="16" />
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5,3 19,12 5,21" />
                      </svg>
                    )}
                  </motion.button>

                  <div className="flex-1 space-y-1.5">
                    <div className="relative h-2 overflow-hidden rounded-full bg-zinc-800">
                      <motion.div
                        animate={{ width: playing ? "100%" : "0%" }}
                        transition={{ duration: 8, ease: "linear" }}
                        className="h-full rounded-full bg-gradient-to-r from-primary to-accent-blue"
                      />
                    </div>
                    <div className="flex justify-between text-[10px] text-text-tertiary">
                      <span>0:00</span>
                      <span>3:05</span>
                    </div>
                  </div>
                </div>

                <div className="h-16">
                  <FrequencyBars playing={playing} color="#44f3d0" barCount={48} />
                </div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  className="mt-4 flex items-center gap-3 rounded-lg bg-primary/5 p-3"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#44f3d0" strokeWidth="2">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-primary">Harmonic Match Confirmed</p>
                    <p className="text-[10px] text-text-tertiary">A Minor → C Major · Camelot 8A → 8B</p>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mx-auto mt-16 max-w-3xl space-y-6"
        >
          <div className="text-center">
            <span className="text-xs font-semibold uppercase tracking-[0.25em] text-text-tertiary">
              — Watch a real transition analyzed by MixMind —
            </span>
          </div>

          <VideoDemo
            onPlayStateChange={handlePlayStateChange}
            onTimeUpdate={handleTimeUpdate}
          />

          <TransitionVisualizer
            playing={videoPlaying}
            currentTime={videoTime}
          />
        </motion.div>
      </div>
    </SectionWrapper>
  );
}