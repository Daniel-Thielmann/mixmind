"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Waves, Activity, Layout } from "lucide-react";
import { formatDuration, formatEnergy, resolveMediaUrl } from "@/lib/format";
import type { AudioAnalysis, ImageAsset } from "@/types";

interface TrackCardProps {
  title: string;
  analysis: AudioAnalysis;
  waveform?: ImageAsset;
  spectrogram?: ImageAsset;
}

type ViewMode = "waveform" | "spectrogram" | "both";

export function TrackCard({
  title,
  analysis,
  waveform,
  spectrogram,
}: TrackCardProps) {
  const [view, setView] = useState<ViewMode>("waveform");

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7"
    >
      <header className="mb-5 flex items-center justify-between gap-3 flex-col">
        <h3 className="text-lg font-semibold text-text">{title}</h3>
        <p className="mt-2 text-xs uppercase tracking-[0.15em] text-text-secondary leading-5 truncate max-w-full">
          {analysis.filename}
        </p>
      </header>

      {/* Alterado para 4 colunas em telas maiores para caber a Key */}
      <dl className="grid grid-cols-2 md:grid-cols-4 gap-3 rounded-xl border border-zinc-800 bg-zinc-900/65 p-4 text-sm">
        <Metric label="BPM" value={analysis.bpm.toFixed(2)} />
        {/* Novo Componente para a Roda de Camelot */}
        <CamelotMetric label="Key" value={analysis.camelot || "N/A"} />
        <Metric label="Duration" value={formatDuration(analysis.duration)} />
        <Metric label="Energy" value={formatEnergy(analysis.energy)} />
      </dl>

      <div className="mt-6">
        <div className="mb-4 grid grid-cols-3 gap-1 rounded-xl border border-zinc-800 bg-zinc-900/40 p-1">
          {[
            { key: "waveform" as const, icon: Waves, label: "Waveform" },
            { key: "spectrogram" as const, icon: Activity, label: "Spectrogram" },
            { key: "both" as const, icon: Layout, label: "Both" },
          ].map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setView(tab.key)}
              className={`flex items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
                view === tab.key
                  ? "bg-zinc-800 text-text shadow-sm"
                  : "text-text-secondary/60 hover:text-text/80"
              }`}
            >
              <tab.icon className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="space-y-4">
          {(view === "waveform" || view === "both") && (
            <ImageBlock
              title="Waveform"
              image={waveform}
              alt={`${title} waveform`}
            />
          )}
          {(view === "spectrogram" || view === "both") && (
            <ImageBlock
              title="Spectrogram"
              image={spectrogram}
              alt={`${title} spectrogram`}
            />
          )}
        </div>
      </div>
    </motion.section>
  );
}

function ImageBlock({
  title,
  image,
  alt,
}: {
  title: string;
  image?: ImageAsset;
  alt: string;
}) {
  return (
    <figure>
      <figcaption className="mb-2 text-xs uppercase tracking-[0.18em] text-text-secondary">
        {title}
      </figcaption>

      <div className="overflow-hidden rounded-lg border border-zinc-800 bg-black/40">
        {image?.image_path ? (
          <img
            src={resolveMediaUrl(image.image_path)}
            alt={alt}
            loading="lazy"
            className="block w-full object-contain"
            onError={(e) => {
              console.error(
                "Failed to load image:",
                resolveMediaUrl(image.image_path),
              );
              e.currentTarget.style.display = "none";
            }}
          />
        ) : (
          <div className="flex h-64 items-center justify-center text-sm text-zinc-500">
            Image not available
          </div>
        )}
      </div>
    </figure>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-[0.13em] text-text-secondary">
        {label}
      </dt>
      <dd className="mt-1 font-semibold text-text">{value}</dd>
    </div>
  );
}

// Novo componente com estilização Neon Blue para destacar o código Camelot
function CamelotMetric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-[0.13em] text-text-secondary">
        {label}
      </dt>
      <dd className="mt-1">
        <span className="inline-flex items-center justify-center rounded bg-cyan-950/40 px-2 py-0.5 text-sm font-bold tracking-widest text-cyan-400 border border-cyan-800/50 shadow-[0_0_10px_rgba(34,211,238,0.3)]">
          {value}
        </span>
      </dd>
    </div>
  );
}