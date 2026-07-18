"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";
import { FrequencyBars } from "./FrequencyBars";

const FADE_UP = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.6, ease: [0.25, 0.1, 0.25, 1] as const },
  }),
};

export function Hero() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 pb-20 pt-24">
      <BackgroundEffects />
      <Particles />

      <div className="relative z-10 mx-auto flex w-full max-w-7xl flex-col items-center gap-16 lg:flex-row lg:items-center">
        <div className="flex-1 text-center lg:text-left">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-xs font-medium text-primary"
          >
            <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse-slow" />
            AI-Powered DJ Analysis Platform
          </motion.div>

          <motion.h1
            custom={0}
            variants={FADE_UP}
            initial="hidden"
            animate="visible"
            className="text-4xl font-bold leading-tight tracking-tight md:text-6xl lg:text-7xl"
          >
            The AI That{" "}
            <span className="bg-gradient-to-r from-primary via-primary-dark to-accent-blue bg-clip-text text-transparent">
              Understands
            </span>{" "}
            Your Mix
          </motion.h1>

          <motion.p
            custom={1}
            variants={FADE_UP}
            initial="hidden"
            animate="visible"
            className="mx-auto mt-6 max-w-lg text-base leading-relaxed text-text-secondary md:text-lg lg:mx-0"
          >
            Upload your tracks. Let MixMind analyze BPM, energy, harmonic keys, and
            compatibility. Get AI-powered recommendations for seamless DJ transitions.
          </motion.p>

          <motion.div
            custom={2}
            variants={FADE_UP}
            initial="hidden"
            animate="visible"
            className="mt-8 flex flex-col items-center gap-4 sm:flex-row lg:items-start"
          >
            <motion.a
              href="#upload"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="inline-flex h-12 items-center gap-2 rounded-xl bg-primary px-6 text-sm font-semibold text-background transition-all duration-300 hover:bg-primary-dark hover:shadow-lg hover:shadow-primary/20"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              Start Analyzing
            </motion.a>
            <motion.a
              href="#demo"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="inline-flex h-12 items-center gap-2 rounded-xl border border-border bg-card/50 px-6 text-sm font-medium text-text-secondary transition-all duration-300 hover:border-border-light hover:text-text"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="5,3 19,12 5,21" />
              </svg>
              Watch Demo
            </motion.a>
          </motion.div>

          <motion.div
            custom={3}
            variants={FADE_UP}
            initial="hidden"
            animate="visible"
            className="mt-12 flex items-center gap-8 text-xs text-text-tertiary"
          >
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-7 w-7 rounded-full border-2 border-background bg-gradient-to-br from-primary/40 to-accent-blue/40"
                  />
                ))}
              </div>
              <span>Trusted by DJs worldwide</span>
            </div>
            <div className="hidden sm:block">✦ Free to try</div>
            <div className="hidden sm:block">✦ No account required</div>
          </motion.div>
        </div>

        <motion.div
          custom={1}
          variants={FADE_UP}
          initial="hidden"
          animate="visible"
          className="relative flex-1"
        >
          <HeroMockup />
        </motion.div>
      </div>
    </section>
  );
}

function HeroMockup() {
  return (
    <div className="group relative">
      <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-primary/10 via-accent-blue/5 to-transparent opacity-0 blur-2xl transition-opacity duration-700 group-hover:opacity-100" />

      <div className="relative overflow-hidden rounded-2xl border border-border bg-card p-6 shadow-2xl">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
            <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
            <div className="h-2.5 w-2.5 rounded-full bg-green-500/60" />
          </div>
          <span className="ml-2 text-xs text-text-tertiary">mixmind.ai — analysis</span>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <p className="text-xs text-text-tertiary">Track A</p>
              <p className="text-sm font-medium text-text">Deep House Session</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-text-tertiary">BPM</p>
              <p className="text-sm font-semibold text-primary">124</p>
            </div>
          </div>

          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <p className="text-xs text-text-tertiary">Track B</p>
              <p className="text-sm font-medium text-text">Melodic Techno Mix</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-text-tertiary">BPM</p>
              <p className="text-sm font-semibold text-accent-blue">126</p>
            </div>
          </div>

          <div className="rounded-xl bg-background p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-medium text-primary">Compatibility Score</span>
              <span className="text-lg font-bold text-primary">94%</span>
            </div>
            <div className="mb-3 h-2 overflow-hidden rounded-full bg-zinc-800">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: "94%" }}
                transition={{ duration: 1.5, delay: 0.5, ease: "easeOut" }}
                className="h-full rounded-full bg-gradient-to-r from-primary to-accent-blue"
              />
            </div>
            <div className="flex h-12 items-end gap-[2px]">
              <FrequencyBars playing={true} color="#44f3d0" barCount={24} />
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-text-tertiary">
            <span>⚡ Harmonic: A m → C Maj</span>
            <span>⚡ Energy: 78% → 85%</span>
            <span>⚡ Camelot: 8A → 8B</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function BackgroundEffects() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-gradient-to-b from-primary/10 to-transparent opacity-30 blur-3xl animate-breathe" />
      <div className="absolute right-0 top-1/4 h-[400px] w-[400px] rounded-full bg-gradient-to-b from-accent-blue/8 to-transparent opacity-20 blur-3xl animate-float" />
      <div className="absolute bottom-0 left-1/4 h-[300px] w-[300px] rounded-full bg-gradient-to-b from-accent-purple/5 to-transparent opacity-20 blur-3xl animate-glow" />
    </div>
  );
}

function Particles() {
  const particles = useMemo(() =>
    Array.from({ length: 20 }, (_, i) => ({
      id: i,
      left: `${(i * 17 + 3) % 100}%`,
      top: `${(i * 13 + 7) % 100}%`,
      duration: ((i * 0.7 + 3) % 4) + 3,
      delay: (i * 0.3) % 3,
    })),
  []);

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute h-1 w-1 rounded-full bg-primary/30"
          style={{
            left: p.left,
            top: p.top,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0, 0.5, 0],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            delay: p.delay,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}
