"use client";

import { motion } from "framer-motion";
import { ArrowRight, AudioLines, Sparkles } from "lucide-react";

export function UploadSection() {
  return (
    <section id="analyzer" className="relative overflow-hidden py-24 md:py-28">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-0 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-4xl overflow-hidden rounded-[2rem] border border-primary/20 bg-card/70 px-6 py-14 text-center shadow-2xl shadow-primary/5 backdrop-blur-xl md:px-16 md:py-20"
        >
          <div className="mx-auto mb-7 flex h-14 w-14 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 text-primary">
            <AudioLines size={25} />
          </div>
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            Your complete mixing workspace
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            MixMind{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Analyzer
            </span>
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-text-secondary md:text-lg">
            Upload any two songs. Receive a complete AI transition analysis and preview the generated transition before your live set.
          </p>
          <motion.a
            href="/analyzer"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="mt-9 inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3.5 font-semibold text-background shadow-lg shadow-primary/15"
          >
            <Sparkles size={17} /> Open Analyzer <ArrowRight size={17} />
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
}
