"use client";

import { ArrowRight, AudioLines, Music, Upload } from "lucide-react";
import { DepthCard, ScrollReveal3D } from "./scroll-motion";
import { Button } from "@/components/ui/button";

export function UploadSection() {
  return (
    <section id="analyzer" className="relative overflow-hidden py-24 md:py-28">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-0 h-100 w-100 -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        <ScrollReveal3D
          className="mx-auto max-w-4xl overflow-hidden rounded-4xl border border-primary/20 bg-card/70 px-6 py-14 text-center shadow-2xl shadow-primary/5 backdrop-blur-xl md:px-16 md:py-20"
        >
          <div className="mx-auto mb-7 flex h-14 w-14 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 text-primary">
            <AudioLines size={25} />
          </div>
          <span className="mb-4 inline-block text-xs font-semibold uppercase tracking-[0.25em] text-primary">
            New — Spotify integration
          </span>
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            MixMind{" "}
            <span className="bg-linear-to-r from-primary to-accent-blue bg-clip-text text-transparent">
              Analyzer
            </span>
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-text-secondary md:text-lg">
            Connect Spotify and select two tracks without downloading MP3 files, or upload your own audio. Both paths use the same MixMind transition pipeline.
          </p>
          <div className="mt-9 flex flex-col justify-center gap-3 [perspective:900px] sm:flex-row">
            <DepthCard index={0}><Button asChild size="lg"><a href="/analyzer?source=spotify"><Music size={17} /> Try with Spotify <ArrowRight size={17} /></a></Button></DepthCard>
            <DepthCard index={1}><Button asChild size="lg" variant="outline"><a href="/analyzer?source=manual"><Upload size={17} /> Upload audio files</a></Button></DepthCard>
          </div>
        </ScrollReveal3D>
      </div>
    </section>
  );
}
