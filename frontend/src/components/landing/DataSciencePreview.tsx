"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";

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
            {HEARD.map((item, i) => <motion.span key={item} initial={{ opacity: 0, y: 8 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * .08 }} className="rounded-full border border-border px-4 py-2 text-sm text-text">{item}</motion.span>)}
          </div>
          <motion.div initial={{ height: 0 }} whileInView={{ height: 64 }} viewport={{ once: true }} transition={{ duration: .8, delay: .25 }} className="mx-auto my-7 w-px bg-gradient-to-b from-border to-primary" />
          <p className="relative text-sm font-medium text-primary">What MixMind sees</p>
          <div className="relative mx-auto mt-6 flex max-w-3xl flex-wrap justify-center gap-3">
            {SEEN.map((item, i) => <motion.span key={item} initial={{ opacity: 0, scale: .92 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: .35 + i * .07 }} className="rounded-full border border-primary/20 bg-primary/5 px-4 py-2 text-sm text-text shadow-[0_0_24px_rgba(68,243,208,0.05)]">{item}</motion.span>)}
          </div>
          <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 1.1 }} className="relative mt-12 text-xl font-semibold md:text-2xl">Then we connect everything.</motion.p>
          <div className="relative mx-auto mt-7 flex max-w-xl items-center gap-4">
            <div className="h-3 w-3 rounded-full bg-primary shadow-[0_0_24px_#44f3d0]" />
            <motion.div initial={{ scaleX: 0 }} whileInView={{ scaleX: 1 }} viewport={{ once: true }} transition={{ duration: 1.2, delay: .7 }} className="h-px flex-1 origin-left bg-gradient-to-r from-primary via-white to-accent-blue" />
            <div className="h-3 w-3 rounded-full bg-accent-blue shadow-[0_0_24px_#3b82f6]" />
          </div>
        </div>
      </div>
    </SectionWrapper>
  );
}
