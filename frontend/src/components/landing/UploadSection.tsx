"use client";

import { motion } from "framer-motion";
import { UploadForm } from "@/components/upload-form";

export function UploadSection() {
  return (
    <section id="upload" className="relative overflow-hidden py-24 md:py-32">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-0 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-12 text-center"
        >
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            Try It Now
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            Analyze Your{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Tracks
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-text-secondary">
            Drop your audio files below and let MixMind&apos;s AI engine do the rest.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.15 }}
        >
          <UploadForm />
        </motion.div>
      </div>
    </section>
  );
}