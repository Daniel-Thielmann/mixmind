"use client";

import { motion, useTransform, type MotionValue } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { DepthCard, ScrollScene } from "./scroll-motion";

const HEARD = ["BPM", "Key", "Feeling", "Energy"];
const SEEN = ["Harmonic compatibility", "Phrase alignment", "Bass collision", "Vocal clash", "Groove continuity", "Dynamic energy", "Transition confidence", "Crowd impact"];

export function DataSciencePreview() {
  return (
    <SectionWrapper className="border-t border-border/50 py-24 md:py-28">
      <div className="mx-auto max-w-6xl px-6 text-center">
        <span className="text-xs font-semibold uppercase tracking-[0.25em] text-primary">Beyond the waveform</span>
        <h2 className="mx-auto mt-5 max-w-3xl text-3xl font-bold tracking-tight md:text-5xl">You hear the music. <span className="text-primary">MixMind reveals what connects it.</span></h2>
        <p className="mx-auto mt-5 max-w-xl text-text-secondary">AI does not replace your instinct. It gives your instinct another layer of perception.</p>

        <div className="relative mt-16 overflow-hidden rounded-[2rem] border border-border bg-card/50 px-5 py-12 md:px-12 md:py-16">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(68,243,208,0.09),transparent_55%)]" />
          <p className="relative text-sm font-medium text-text-secondary">What DJs hear</p>
          <div className="relative mt-5 flex flex-wrap justify-center gap-3">
            {HEARD.map((item, i) => <DepthCard key={item} index={i} className="rounded-full border border-border px-4 py-2 text-sm text-text">{item}</DepthCard>)}
          </div>
          <motion.div initial={{ height: 0 }} whileInView={{ height: 64 }} viewport={{ once: true }} transition={{ duration: .8, delay: .25 }} className="mx-auto my-7 w-px bg-gradient-to-b from-border to-primary" />
          <p className="relative text-sm font-medium text-primary">What MixMind sees</p>
          <div className="relative mx-auto mt-6 flex max-w-3xl flex-wrap justify-center gap-3">
            {SEEN.map((item, i) => <DepthCard key={item} index={i} className="rounded-full border border-primary/20 bg-primary/5 px-4 py-2 text-sm text-text shadow-[0_0_24px_rgba(68,243,208,0.05)]">{item}</DepthCard>)}
          </div>
          <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 1.1 }} className="relative mt-12 text-xl font-semibold md:text-2xl">Then we connect everything.</motion.p>
          <CompatibilityConvergence />
        </div>
      </div>
    </SectionWrapper>
  );
}

function CompatibilityConvergence() {
  return <ScrollScene className="relative mx-auto mt-7 max-w-xl py-8">{({ smoothProgress, reducedMotion }) => <ConvergenceLayers progress={smoothProgress} reducedMotion={reducedMotion} />}</ScrollScene>;
}

function ConvergenceLayers({ progress, reducedMotion }: { progress: MotionValue<number>; reducedMotion: boolean }) {
  const leftX = useTransform(progress, [0.1, 0.65], [reducedMotion ? 0 : -34, 0]);
  const rightX = useTransform(progress, [0.1, 0.65], [reducedMotion ? 0 : 34, 0]);
  const leftRotate = useTransform(progress, [0.1, 0.65], [reducedMotion ? 0 : 6, 0]);
  const rightRotate = useTransform(progress, [0.1, 0.65], [reducedMotion ? 0 : -6, 0]);
  const glow = useTransform(progress, [0.2, 0.7], [0.15, 0.8]);
  return <div className="flex items-center gap-4 [perspective:800px]">
    <motion.div style={{ x: leftX, rotateY: leftRotate }} className="rounded-lg border border-primary/25 bg-primary/10 px-3 py-2 text-xs font-semibold text-primary">Track A</motion.div>
    <div className="relative h-px flex-1 overflow-visible bg-gradient-to-r from-primary via-white to-accent-blue"><motion.div aria-hidden style={{ opacity: glow }} className="absolute -inset-y-3 inset-x-0 bg-gradient-to-r from-primary/20 via-white/25 to-accent-blue/20 blur-lg" /></div>
    <motion.div style={{ x: rightX, rotateY: rightRotate }} className="rounded-lg border border-accent-blue/25 bg-accent-blue/10 px-3 py-2 text-xs font-semibold text-accent-blue">Track B</motion.div>
  </div>;
}
