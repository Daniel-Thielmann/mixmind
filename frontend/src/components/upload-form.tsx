"use client";

import { useState } from "react";

export function UploadForm() {
  const [trackA, setTrackA] = useState<string>();
  const [trackB, setTrackB] = useState<string>();
  const [loading, setLoading] = useState(false);

  async function handleAnalyze() {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 2000));
    setLoading(false);
  }

  return (
    <div className="mt-12 w-full space-y-6">
      <div className="grid gap-6 md:grid-cols-2">
        <UploadCard
          label="Track A"
          fileName={trackA}
          onFile={(f) => setTrackA(f.name)}
        />
        <UploadCard
          label="Track B"
          fileName={trackB}
          onFile={(f) => setTrackB(f.name)}
        />
      </div>

      <button
        onClick={handleAnalyze}
        disabled={!trackA || !trackB || loading}
        className="w-full rounded-xl bg-success px-6 py-4 text-lg font-bold text-black transition hover:brightness-110 disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-black border-t-transparent" />
            Analyzing...
          </span>
        ) : (
          "Analyze Tracks"
        )}
      </button>
    </div>
  );
}

function UploadCard({
  label,
  fileName,
  onFile,
}: {
  label: string;
  fileName?: string;
  onFile: (file: File) => void;
}) {
  const [dragging, setDragging] = useState(false);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onFile(file);
  }

  function handleClick() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "audio/*";
    input.onchange = () => {
      const file = input.files?.[0];
      if (file) onFile(file);
    };
    input.click();
  }

  return (
    <div className="rounded-2xl border border-zinc-800 bg-card p-6 shadow-2xl md:p-8">
      <h4 className="mb-6 text-xl font-semibold">{label}</h4>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition ${
          dragging
            ? "border-primary bg-primary/10"
            : "border-zinc-700 bg-zinc-900/50 hover:border-zinc-600"
        }`}
      >
        {fileName ? (
          <p className="text-sm text-text">{fileName}</p>
        ) : (
          <>
            <span className="mb-2 text-3xl text-zinc-600">+</span>
            <p className="text-sm text-text-secondary">
              Drop audio file here
            </p>
            <p className="mt-1 text-xs text-zinc-600">
              or click to browse
            </p>
          </>
        )}
      </div>
    </div>
  );
}
