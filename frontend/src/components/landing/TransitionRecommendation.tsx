"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { MOCK_TRACK_A, MOCK_TRACK_B, MOCK_COMPATIBILITY } from "./mock-data";

export function TransitionRecommendation() {
  return (
    <SectionWrapper className="border-t border-border/50 py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-16 text-center"
        >
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            AI Recommendation
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            Intelligent{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Transition Analysis
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            See how MixMind analyzes harmonic compatibility, energy flow, and tempo alignment between your tracks.
          </p>
        </motion.div>

        <div className="grid gap-8 lg:grid-cols-3">
          <TrackCard track={MOCK_TRACK_A} label="Track A" color="text-primary" />
          <FlowCenter />
          <TrackCard track={MOCK_TRACK_B} label="Track B" color="text-accent-blue" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mx-auto mt-12 max-w-3xl"
        >
          <div className="rounded-2xl border border-border bg-card p-6 md:p-8">
            <h3 className="mb-6 text-center text-lg font-semibold text-text">Compatibility Matrix</h3>
            <div className="grid gap-4 sm:grid-cols-3">
              <MatchCard
                label="Harmonic Match"
                matched={MOCK_COMPATIBILITY.harmonicMatch}
                detail={`${MOCK_TRACK_A.camelot} → ${MOCK_TRACK_B.camelot}`}
                delay={0}
              />
              <MatchCard
                label="BPM Match"
                matched={MOCK_COMPATIBILITY.bpmMatch}
                detail={`${MOCK_TRACK_A.bpm} → ${MOCK_TRACK_B.bpm} (Δ${MOCK_COMPATIBILITY.bpmDiff})`}
                delay={0.1}
              />
              <MatchCard
                label="Energy Match"
                matched={MOCK_COMPATIBILITY.energyMatch}
                detail={`${Math.round(MOCK_TRACK_A.energy * 100)}% → ${Math.round(MOCK_TRACK_B.energy * 100)}%`}
                delay={0.2}
              />
            </div>

            <div className="mt-6 rounded-xl bg-gradient-to-r from-primary/10 via-accent-blue/5 to-transparent p-4 text-center">
              <p className="text-xs text-text-tertiary">Overall Compatibility</p>
              <p className="text-3xl font-bold text-primary">{MOCK_COMPATIBILITY.score}%</p>
              <p className="text-xs text-text-tertiary">Seamless transition recommended</p>
            </div>
          </div>
        </motion.div>
      </div>
    </SectionWrapper>
  );
}

function TrackCard({ track, label, color }: { track: typeof MOCK_TRACK_A; label: string; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="rounded-2xl border border-border bg-card p-6 transition-all duration-500 hover:border-border-light"
    >
      <span className={`mb-3 inline-block text-xs font-semibold uppercase tracking-[0.2em] ${color}`}>
        {label}
      </span>
      <h3 className="mb-1 text-lg font-semibold text-text">{track.title}</h3>
      <p className="mb-4 text-xs text-text-tertiary">{track.artist}</p>
      <div className="space-y-3">
        <InfoRow label="BPM" value={String(track.bpm)} />
        <InfoRow label="Key" value={track.key} />
        <InfoRow label="Camelot" value={track.camelot} />
        <InfoRow label="Energy" value={`${Math.round(track.energy * 100)}%`} />
        <InfoRow label="Duration" value={`${Math.floor(track.duration / 60)}:${String(track.duration % 60).padStart(2, "0")}`} />
      </div>
    </motion.div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-border/50 pb-2 text-sm">
      <span className="text-text-tertiary">{label}</span>
      <span className="font-medium text-text">{value}</span>
    </div>
  );
}

function FlowCenter() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="flex flex-col items-center justify-center gap-3 py-6"
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#44f3d0" strokeWidth="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </div>
      <div className="h-16 w-px bg-gradient-to-b from-primary/40 via-accent-blue/40 to-transparent" />
      <div className="rounded-lg bg-card px-4 py-2 text-center">
        <p className="text-xs font-medium text-primary">AI Analysis</p>
        <p className="text-[10px] text-text-tertiary">Computing compatibility...</p>
      </div>
      <div className="h-16 w-px bg-gradient-to-b from-accent-blue/40 to-primary/40" />
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-blue/10">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </div>
    </motion.div>
  );
}

function MatchCard({ label, matched, detail, delay }: { label: string; matched: boolean; detail: string; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="rounded-xl border border-border bg-background p-4 text-center"
    >
      <div className="mb-2 flex justify-center">
        {matched ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-success/10">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#21d969" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-danger/10">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5b6e" strokeWidth="2.5">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </div>
        )}
      </div>
      <p className="text-xs font-medium text-text">{label}</p>
      <p className="mt-0.5 text-[10px] text-text-tertiary">{detail}</p>
    </motion.div>
  );
}