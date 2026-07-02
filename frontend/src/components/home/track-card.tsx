import { formatDuration, formatEnergy, resolveMediaUrl } from "@/lib/format";
import type { AudioAnalysis, ImageAsset } from "@/types";

interface TrackCardProps {
  title: string;
  analysis: AudioAnalysis;
  waveform?: ImageAsset;
  spectrogram?: ImageAsset;
}

export function TrackCard({
  title,
  analysis,
  waveform,
  spectrogram,
}: TrackCardProps) {
  return (
    <section className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7">
      <header className="mb-5 flex items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-text">{title}</h3>

        <span className="truncate text-xs uppercase tracking-[0.2em] text-text-secondary">
          {analysis.filename}
        </span>
      </header>

      <dl className="grid grid-cols-3 gap-3 rounded-xl border border-zinc-800 bg-zinc-900/65 p-4 text-sm">
        <Metric label="BPM" value={analysis.bpm.toFixed(2)} />
        <Metric label="Duration" value={formatDuration(analysis.duration)} />
        <Metric label="Energy" value={formatEnergy(analysis.energy)} />
      </dl>

      <div className="mt-6 space-y-5">
        <ImageBlock
          title="Waveform"
          image={waveform}
          alt={`${title} waveform`}
        />

        <ImageBlock
          title="Spectrogram"
          image={spectrogram}
          alt={`${title} spectrogram`}
        />
      </div>
    </section>
  );
}

interface ImageBlockProps {
  title: string;
  image?: ImageAsset;
  alt: string;
}

function ImageBlock({ title, image, alt }: ImageBlockProps) {
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
          <div className="flex h-44 items-center justify-center text-sm text-zinc-500">
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
