"use client";

interface FeatureBadgeProps {
  variant?: "coming-soon" | "future-feature";
}

export function FeatureBadge({ variant = "coming-soon" }: FeatureBadgeProps) {
  return (
    <div className="inline-flex max-w-lg items-center gap-2.5 rounded-full border border-primary/15 bg-primary/[0.04] px-4 py-2 backdrop-blur-sm">
      <span className="shrink-0 rounded-full bg-primary/15 px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-wider text-primary">
        {variant === "coming-soon" ? "Coming Soon" : "Future Feature"}
      </span>
      <span className="text-[11px] leading-relaxed text-text-secondary">
        Upload any two songs and let MixMind generate a transition preview before your set.
      </span>
    </div>
  );
}
