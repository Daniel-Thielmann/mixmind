"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { MOCK_TECHNOLOGIES } from "./mock-data";
import { Code2, Zap, Database, Brain, MessageSquare, Sigma, Container, Globe } from "lucide-react";

const ICON_MAP: Record<string, React.ElementType> = {
  Code2,
  Zap,
  Database,
  Brain,
  MessageSquare,
  Sigma,
  Container,
  Globe,
};

const CATEGORIES = ["Backend", "ML", "Infra", "Frontend"] as const;

export function Technologies() {
  return (
    <SectionWrapper id="technologies" className="border-t border-border/50 py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-16 text-center"
        >
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            Technology
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            Built with{" "}
            <span className="bg-gradient-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Modern Stack
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            A robust foundation of cutting-edge technologies powering every analysis and recommendation.
          </p>
        </motion.div>

        <div className="space-y-6">
          {CATEGORIES.map((category, catIndex) => {
            const techs = MOCK_TECHNOLOGIES.filter((t) => t.category === category);
            return (
              <motion.div
                key={category}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: catIndex * 0.1, duration: 0.5 }}
              >
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-text-tertiary">
                  {category}
                </h3>
                <div className="flex flex-wrap gap-3">
                  {techs.map((tech, techIndex) => {
                    const Icon = ICON_MAP[tech.icon] || Code2;
                    return (
                      <motion.div
                        key={tech.name}
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ delay: (catIndex * 0.1) + (techIndex * 0.05), duration: 0.3 }}
                        whileHover={{ y: -2, scale: 1.02 }}
                        className="flex items-center gap-2.5 rounded-xl border border-border bg-card px-4 py-2.5 transition-all duration-300 hover:border-primary/20 hover:bg-card-hover"
                      >
                        <Icon size={16} className="text-primary" />
                        <span className="text-sm font-medium text-text">{tech.name}</span>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </SectionWrapper>
  );
}