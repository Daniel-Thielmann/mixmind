"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { MOCK_ROADMAP } from "./mock-data";

export function Roadmap() {
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
            Roadmap
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            What&apos;s{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Coming Next
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            MixMind is evolving rapidly. Here&apos;s what we&apos;re building to make your DJ workflow even more powerful.
          </p>
        </motion.div>

        <div className="relative mx-auto max-w-4xl">
          <div className="absolute left-6 top-0 h-full w-px bg-border md:left-1/2 md:-translate-x-px" />

          <div className="space-y-12">
            {MOCK_ROADMAP.map((milestone, index) => (
              <motion.div
                key={milestone.sprint}
                initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.12, duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
                className={`relative flex flex-col gap-4 md:flex-row ${
                  index % 2 === 0 ? "md:flex-row" : "md:flex-row-reverse"
                }`}
              >
                <div className="flex-1" />

                <div className="absolute left-6 top-0 z-10 flex h-12 w-12 items-center justify-center rounded-full border-2 border-border bg-background md:left-1/2 md:-translate-x-1/2">
                  {milestone.status === "completed" ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#21d969" strokeWidth="2.5">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : milestone.status === "in-progress" ? (
                    <div className="h-3 w-3 rounded-full bg-primary animate-pulse-slow" />
                  ) : (
                    <div className="h-3 w-3 rounded-full bg-text-tertiary" />
                  )}
                </div>

                <div className="flex-1 pl-16 md:pl-0 md:pr-12 md:text-right">
                  <div
                    className={`rounded-2xl border border-border bg-card p-5 transition-all duration-500 hover:border-border-light ${
                      milestone.status === "in-progress" ? "border-primary/20" : ""
                    }`}
                  >
                    <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-primary">
                      {milestone.sprint}
                    </span>
                    <h3 className="mb-1 mt-1 text-base font-semibold text-text">{milestone.title}</h3>
                    <ul className="mt-2 space-y-1">
                      {milestone.items.map((item) => (
                        <li key={item} className="flex items-start gap-2 text-xs text-text-secondary">
                          <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-text-tertiary" />
                          {item}
                        </li>
                      ))}
                    </ul>
                    <span
                      className={`mt-3 inline-block rounded-full px-2 py-0.5 text-[10px] font-medium ${
                        milestone.status === "completed"
                          ? "bg-success/10 text-success"
                          : milestone.status === "in-progress"
                            ? "bg-primary/10 text-primary"
                            : "bg-zinc-800 text-text-tertiary"
                      }`}
                    >
                      {milestone.status === "completed" ? "Completed" : milestone.status === "in-progress" ? "In Progress" : "Planned"}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </SectionWrapper>
  );
}