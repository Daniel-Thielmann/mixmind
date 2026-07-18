"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { MOCK_FEATURES } from "./mock-data";
import { Sparkles, Music, Waves, Activity, Route, Timer } from "lucide-react";

const ICON_MAP: Record<string, React.ElementType> = {
  Sparkles,
  Music,
  Waves,
  Activity,
  Route,
  Timer,
};

export function Features() {
  return (
    <SectionWrapper id="features" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-16 text-center"
        >
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            Features
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            Everything a{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Modern DJ
            </span>{" "}
            Needs
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            From AI-powered analysis to professional transition planning — MixMind equips you with tools that elevate your sets.
          </p>
        </motion.div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {MOCK_FEATURES.map((feature, index) => {
            const Icon = ICON_MAP[feature.icon] || Sparkles;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08, duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
                whileHover={{ y: -4 }}
                className="group rounded-2xl border border-border bg-card p-6 transition-all duration-500 hover:border-primary/20 hover:bg-card-hover hover:shadow-lg hover:shadow-primary/5"
              >
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-accent-blue/10 text-primary transition-all duration-300 group-hover:from-primary/20 group-hover:to-accent-blue/20">
                  <Icon size={20} />
                </div>
                <h3 className="mb-2 text-base font-semibold text-text">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-text-secondary">{feature.description}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </SectionWrapper>
  );
}