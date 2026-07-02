"use client";

import { useState } from "react";

import { Dashboard } from "@/components/home/dashboard";
import { UploadCard } from "@/components/upload/upload-card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { apiService } from "@/services/api";
import type { UploadAnalysisResponse, UploadStatus } from "@/types";

const FRIENDLY_VALIDATION_MESSAGE =
  "Please select both tracks before analyzing.";
const FRIENDLY_ERROR_MESSAGE =
  "Unable to analyze the selected tracks. Please try again.";

export function UploadForm() {
  const [trackA, setTrackA] = useState<File>();
  const [trackB, setTrackB] = useState<File>();
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadAnalysisResponse | null>(null);
  const isBusy = status === "uploading" || status === "processing";

  async function handleAnalyze() {
    if (!trackA || !trackB) {
      setResult(null);
      setStatus("error");
      setError(FRIENDLY_VALIDATION_MESSAGE);
      return;
    }

    setStatus("uploading");
    setError(null);
    setResult(null);

    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, 0);
    });

    try {
      setStatus("processing");
      const response = await apiService.analyzeTracks(trackA, trackB);
      setResult(response);
      setStatus("success");
    } catch (requestError) {
      setResult(null);
      setStatus("error");
      setError(
        requestError instanceof Error
          ? requestError.message
          : FRIENDLY_ERROR_MESSAGE,
      );
    }
  }

  return (
    <section className="mt-12 w-full">
      <div className="rounded-3xl border border-zinc-800 bg-card/65 p-6 shadow-[0_25px_80px_-45px_rgba(0,0,0,1)] backdrop-blur md:p-8">
        <div className="grid gap-6 lg:grid-cols-2">
          <UploadCard
            label="Track A"
            fileName={trackA?.name}
            onFile={(file) => setTrackA(file)}
          />
          <UploadCard
            label="Track B"
            fileName={trackB?.name}
            onFile={(file) => setTrackB(file)}
          />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={!trackA || !trackB || isBusy}
          aria-busy={isBusy}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-success px-6 py-4 text-base font-bold text-black transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-55"
        >
          {status === "processing" ? (
            <>
              <LoadingSpinner />
              Analyzing tracks...
            </>
          ) : status === "uploading" ? (
            <>
              <LoadingSpinner />
              Uploading tracks...
            </>
          ) : (
            "Analyze"
          )}
        </button>

        {error ? (
          <p className="mt-4 rounded-xl border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-200">
            {error}
          </p>
        ) : null}
      </div>

      {result ? <Dashboard result={result} /> : null}
    </section>
  );
}
