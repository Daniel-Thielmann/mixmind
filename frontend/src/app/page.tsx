import { UploadForm } from "@/components/upload-form";

export default function Home() {
  return (
    <section className="w-full">
      <div className="mx-auto max-w-5xl text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-primary">
          MixMind AI Dashboard
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-6xl">
          Analyze Two Tracks. Compare Fast.
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-text-secondary md:text-lg">
          Upload Track A and Track B to inspect tempo, energy, waveforms,
          spectrograms, and compatibility in one focused DJ workspace.
        </p>
      </div>
      <UploadForm />
    </section>
  );
}
