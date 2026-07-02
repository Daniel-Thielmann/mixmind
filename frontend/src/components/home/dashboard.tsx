import type { UploadAnalysisResponse } from "@/types";

import { CompatibilityCard } from "./compatibility-card";
import { TrackCard } from "./track-card";

interface DashboardProps {
  result: UploadAnalysisResponse;
}

export function Dashboard({ result }: DashboardProps) {
  const waveforms = result.waveforms;
  const spectrograms = result.spectrograms;

  if (!waveforms || !spectrograms) {
    return null;
  }

  return (
    <section className="mt-10 w-full space-y-6">
      <div className="grid gap-6 xl:grid-cols-2">
        <TrackCard
          title="Track A"
          analysis={result.track_a}
          waveform={waveforms.track_a}
          spectrogram={spectrograms.track_a}
        />
        <TrackCard
          title="Track B"
          analysis={result.track_b}
          waveform={waveforms.track_b}
          spectrogram={spectrograms.track_b}
        />
      </div>
      <CompatibilityCard compatibility={result.compatibility} />
    </section>
  );
}
