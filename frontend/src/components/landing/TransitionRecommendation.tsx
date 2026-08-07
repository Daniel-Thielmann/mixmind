"use client";

import { SectionWrapper } from "./SectionWrapper";
import { DepthCard, ScrollReveal3D } from "./scroll-motion";
import { Card } from "@/components/ui/card";

const THOUGHTS = [
  ["I found the cleanest opening.", "Track B begins after Track A releases its vocal phrase."],
  ["The keys want to stay together.", "Their harmonic movement supports a smooth, tension-free blend."],
  ["There is one moment to protect.", "Ease the low end during the overlap to keep the room clear."],
  ["This transition is ready.", "Start the blend at 02:48 and let the energy rise for 32 seconds."],
];

export function TransitionRecommendation() {
  return (
    <SectionWrapper id="ai-recommendation" className="border-t border-border/50 py-24 md:py-28">
      <div className="mx-auto max-w-5xl px-6">
        <div className="text-center">
          <span className="text-xs font-semibold uppercase tracking-[0.25em] text-primary">AI recommendation</span>
          <h2 className="mx-auto mt-5 max-w-3xl text-3xl font-bold tracking-tight md:text-5xl">Not just a score. <span className="text-primary">A reasoned way forward.</span></h2>
          <p className="mx-auto mt-5 max-w-xl text-text-secondary">Watch MixMind turn dozens of invisible signals into one clear decision you can perform.</p>
        </div>
        <div className="mx-auto mt-16 max-w-3xl space-y-4">
          {THOUGHTS.map(([title, body], i) => (
            <DepthCard key={title} index={i} className={`flex ${i % 2 ? "justify-end" : "justify-start"}`}>
              <Card className="max-w-xl rounded-2xl px-5 py-4">
                <p className="font-semibold text-text">{title}</p><p className="mt-1 text-sm leading-relaxed text-text-secondary">{body}</p>
              </Card>
            </DepthCard>
          ))}
          <ScrollReveal3D depth={120} className="mt-8 rounded-2xl border border-primary/25 bg-primary/5 p-6 text-center">
            <p className="text-xs uppercase tracking-[.2em] text-primary">Transition confidence</p><p className="mt-2 text-4xl font-bold text-text">92%</p><p className="mt-2 text-sm text-text-secondary">Smooth, musical and ready for the room.</p>
          </ScrollReveal3D>
        </div>
      </div>
    </SectionWrapper>
  );
}
