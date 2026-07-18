"use client";

interface FeatureBadgeProps {
  variant?: "coming-soon" | "future-feature";
}

export function FeatureBadge({ variant = "coming-soon" }: FeatureBadgeProps) {
  return (
    <div className="relative w-full overflow-hidden rounded-2xl border border-primary/25 bg-linear-to-br from-primary/[0.09] via-card/80 to-accent-blue/[0.06] p-6 text-left shadow-[0_24px_70px_-40px_rgba(68,243,208,0.45)] backdrop-blur-md md:p-7">
      <div className="pointer-events-none absolute -top-24 right-0 h-48 w-48 rounded-full bg-primary/10 blur-3xl" />
      <div className="relative">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-primary/25 bg-primary/15 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-primary">
            {variant === "coming-soon" ? "Coming Soon" : "Future Feature"}
          </span>
          <span className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
            In active development
          </span>
        </div>

        <h3 className="max-w-xl text-xl font-bold tracking-tight text-text md:text-2xl">
          From intelligent analysis to a transition you can actually hear.
        </h3>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-text-secondary">
          MixMind already combines detailed track insights, LLM-powered ideas,
          and step-by-step guidance to show you the best transition, technique,
          and timing for your mix.
        </p>

        <div className="mt-5 rounded-xl border border-primary/20 bg-background/45 p-4 md:flex md:items-center md:gap-4">
          <div className="mb-3 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary md:mb-0">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M9 18V5l12-2v13" />
              <circle cx="6" cy="18" r="3" />
              <circle cx="18" cy="16" r="3" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-text">Automatic MP3 transition previews</p>
            <p className="mt-1 text-xs leading-5 text-text-secondary">
              We&apos;re testing a new upload flow that turns MixMind&apos;s recommendations
              into a ready-to-listen MP3 preview—then connects each blend so you can
              build and audition your complete set before performing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
