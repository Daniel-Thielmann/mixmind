"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { MOCK_DATASCIENCE_CARDS } from "./mock-data";
import {
  BarChart3,
  ScatterChart,
  Network,
  CircleDot,
  Grid3x3,
  Gauge,
  TrendingUp,
  Table2,
} from "lucide-react";

const ICON_MAP: Record<string, React.ElementType> = {
  BarChart3,
  ScatterChart,
  Network,
  CircleDot,
  Grid3x3,
  Gauge,
  TrendingUp,
  Table2,
};

export function DataSciencePreview() {
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
            Data Science
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            Built on{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Machine Learning
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            Advanced audio feature extraction and analysis powering every recommendation. Visualizations coming in the next sprint.
          </p>
        </motion.div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {MOCK_DATASCIENCE_CARDS.map((card, index) => {
            const Icon = ICON_MAP[card.icon] || BarChart3;
            return (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.06, duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
                className="group relative overflow-hidden rounded-xl border border-border bg-card p-5 transition-all duration-500 hover:border-primary/20 hover:bg-card-hover"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 transition-opacity duration-500 group-hover:opacity-100`} />
                <div className="relative">
                  <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-background text-primary">
                    <Icon size={18} />
                  </div>
                  <h3 className="mb-1 text-sm font-semibold text-text">{card.title}</h3>
                  <p className="mb-3 text-xs text-text-tertiary">{card.description}</p>
                  <div className="h-16 rounded-lg bg-background/50 p-2">
                    <div className="flex h-full items-center justify-center">
                      <motion.div
                        animate={{ opacity: [0.3, 0.6, 0.3] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        className="text-[10px] font-medium uppercase tracking-wider text-text-tertiary"
                      >
                        Render in Sprint 3
                      </motion.div>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </SectionWrapper>
  );
}