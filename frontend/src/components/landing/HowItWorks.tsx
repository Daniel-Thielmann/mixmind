"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { HOW_IT_WORKS } from "./mock-data";
import {
  Upload,
  Cpu,
  Brain,
  Music4,
  Sparkles,
} from "lucide-react";

const ICON_MAP: Record<string, React.ElementType> = {
  Upload,
  Cpu,
  Brain,
  Music4,
  Sparkles,
};

export function HowItWorks() {
  return (
    <SectionWrapper id="how-it-works" className="py-24 md:py-28">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-16 text-center"
        >
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            How It Works
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            From Upload to{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Perfect Mix
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            Five steps. Zero hassle. MixMind&apos;s AI engine does the heavy lifting so you can focus on the music.
          </p>
        </motion.div>

        <div className="relative">
          <ConnectionLine />
          <div className="grid gap-6 md:grid-cols-5">
            {HOW_IT_WORKS.map((step, index) => {
              const Icon = ICON_MAP[step.icon] || Upload;
              return (
                <motion.div
                  key={step.step}
                  initial={{ opacity: 0, y: 40 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.12, duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const }}
                  className="group relative rounded-2xl border border-border bg-card p-6 transition-all duration-500 hover:border-primary/20 hover:bg-card-hover"
                >
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary/20">
                    <Icon size={22} />
                  </div>
                  <div className="mb-2 flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/20 text-[10px] font-bold text-primary">
                      {step.step}
                    </span>
                    <h3 className="text-sm font-semibold text-text">{step.title}</h3>
                  </div>
                  <p className="text-xs leading-relaxed text-text-secondary">
                    {step.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </SectionWrapper>
  );
}

function ConnectionLine() {
  return (
    <div className="absolute left-0 right-0 top-1/2 hidden h-px -translate-y-1/2 md:block">
      <svg className="h-full w-full" viewBox="0 0 1000 1" preserveAspectRatio="none">
        <motion.path
          d="M 0 0.5 L 1000 0.5"
          stroke="url(#lineGradient)"
          strokeWidth="1"
          strokeDasharray="4 4"
          fill="none"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.5, ease: "easeInOut" }}
        />
        <defs>
          <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#44f3d0" stopOpacity="0.1" />
            <stop offset="50%" stopColor="#44f3d0" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#44f3d0" stopOpacity="0.1" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}
