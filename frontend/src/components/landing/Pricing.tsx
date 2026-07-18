"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { Check } from "lucide-react";

const PLANS = [
  {
    name: "Free",
    price: "$0",
    description: "Perfect for trying out MixMind",
    features: [
      "Up to 1 analysis per day",
      "Basic BPM & key detection",
      "Waveform preview",
      "Spectrogram preview",
      "Single transition recommendation",
      "Community support",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Starter",
    price: "$12",
    period: "/month",
    description: "For hobbyist DJs getting started",
    features: [
      "Up to 10 analyses per day",
      "Full BPM, key & energy analysis",
      "Waveform & spectrogram export",
      "AI transition strategies",
      "Harmonic compatibility scoring",
      "Email support",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$25",
    period: "/month",
    description: "For professional DJs and producers",
    features: [
      "Unlimited analyses",
      "AI transition strategies",
      "Advanced ML feature extraction",
      "Waveform & spectrogram export",
      "Export analysis reports (PDF/CSV)",
      "DJ execution timeline generation",
      "Priority support",
      "Early access to new features",
    ],
    cta: "Start Free Trial",
    highlighted: true,
    badge: "Most Popular",
  },
  {
    name: "Enterprise",
    price: "$99",
    period: "/month",
    description: "For studios, labels, and teams",
    features: [
      "Everything in Pro",
      "Unlimited team members",
      "Custom API access",
      "Dedicated ML model training",
      "White-label reports",
      "SLA & dedicated support",
      "Custom integrations",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

export function Pricing() {
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
            Pricing
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            Choose Your{" "}
            <span className="bg-linear-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Plan
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
            Start free. Scale as your mixes get better. No hidden fees, no
            surprises.
          </p>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-4">
          {PLANS.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{
                delay: index * 0.08,
                duration: 0.5,
                ease: [0.25, 0.1, 0.25, 1],
              }}
              whileHover={{ y: -4 }}
              className={`relative flex flex-col rounded-2xl border bg-card p-6 transition-all duration-500 ${
                plan.highlighted
                  ? "border-primary/30 shadow-lg shadow-primary/5"
                  : "border-border hover:border-border-light"
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="inline-block rounded-full bg-linear-to-r from-primary to-accent-blue px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-background">
                    {plan.badge}
                  </span>
                </div>
              )}

              <div className="mb-5">
                <h3 className="text-lg font-semibold text-text">{plan.name}</h3>
                <div className="mt-2 flex items-baseline gap-0.5">
                  <span className="text-4xl font-bold text-text">
                    {plan.price}
                  </span>
                  {plan.period && (
                    <span className="text-sm text-text-tertiary">
                      {plan.period}
                    </span>
                  )}
                </div>
                <p className="mt-1 text-xs text-text-secondary">
                  {plan.description}
                </p>
              </div>

              <ul className="mb-6 flex-1 space-y-2.5">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <Check size={14} className="mt-0.5 shrink-0 text-primary" />
                    <span className="text-xs text-text-secondary">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              <motion.a
                href="#"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`flex h-10 items-center justify-center rounded-lg text-sm font-medium transition-all duration-300 ${
                  plan.highlighted
                    ? "bg-primary text-background hover:bg-primary-dark shadow-sm shadow-primary/20"
                    : "border border-border text-text-secondary hover:border-border-light hover:text-text"
                }`}
              >
                {plan.cta}
              </motion.a>
            </motion.div>
          ))}
        </div>
      </div>
    </SectionWrapper>
  );
}
