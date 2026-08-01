"use client";

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, FileAudio, Music, Upload } from "lucide-react";

import { AuthDialog } from "@/components/auth/AuthDialog";
import { Dashboard } from "@/components/home/dashboard";
import { SpotifyAnalyzerSource } from "@/components/spotify/SpotifyAnalyzerSource";
import { UploadCard } from "@/components/upload/upload-card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { SkeletonGrid } from "@/components/ui/Skeleton";
import { loadSpotifyTracks, clearSpotifyTracks } from "@/lib/spotify-storage";
import { apiService } from "@/services/api";
import { analyzeSpotifyTracks } from "@/services/spotify-service";
import { useAuth } from "@/hooks/useAuth";
import type { UploadAnalysisResponse, UploadStatus } from "@/types";
import type { SpotifySelectedTrack } from "@/types/spotify";

const FRIENDLY_VALIDATION_MESSAGE =
  "Please select both tracks before analyzing.";
const FRIENDLY_ERROR_MESSAGE =
  "Unable to analyze the selected tracks. Please try again.";

const STEPS = [
  { key: "fetch", label: "Fetching tracks" },
  { key: "process", label: "Processing audio" },
  { key: "ai", label: "AI generating recommendation" },
  { key: "done", label: "Complete" },
] as const;

type InputMode = "manual" | "spotify";

export function UploadForm() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [mode, setMode] = useState<InputMode>("manual");

  const [trackA, setTrackA] = useState<File>();
  const [trackB, setTrackB] = useState<File>();

  const [spotifyTrackA, setSpotifyTrackA] = useState<SpotifySelectedTrack | null>(null);
  const [spotifyTrackB, setSpotifyTrackB] = useState<SpotifySelectedTrack | null>(null);

  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadAnalysisResponse | null>(null);
  const [showAiPhase, setShowAiPhase] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);

  const isBusy = status === "uploading" || status === "processing";

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams(window.location.search);
      if (params.get("source") === "spotify") setMode("spotify");
      if (params.get("spotify") !== "1") return;
      const stored = loadSpotifyTracks();
      if (!stored) return;
      setMode("spotify");
      setSpotifyTrackA(stored.trackA);
      setSpotifyTrackB(stored.trackB);
      clearSpotifyTracks();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (status !== "processing") return;
    const t = setTimeout(() => setShowAiPhase(true), 3000);
    return () => clearTimeout(t);
  }, [status]);

  let phase = 0;
  if (status === "uploading") phase = 1;
  else if (status === "processing") phase = showAiPhase ? 3 : 2;
  else if (status === "success") phase = 4;

  const handleAnalyze = useCallback(async () => {
    if (!isAuthenticated) {
      setResult(null);
      setStatus("error");
      setError("You need to sign in before running an analysis.");
      setAuthOpen(true);
      return;
    }

    if (mode === "manual") {
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
    } else {
      if (!spotifyTrackA || !spotifyTrackB) {
        setResult(null);
        setStatus("error");
        setError(FRIENDLY_VALIDATION_MESSAGE);
        return;
      }
      setStatus("uploading");
      setError(null);
      setResult(null);
      clearSpotifyTracks();
      await new Promise<void>((resolve) => {
        window.setTimeout(resolve, 0);
      });
      try {
        setStatus("processing");
        const response = await analyzeSpotifyTracks({
          tracks: [
            { position: "track_a", spotify_track_id: spotifyTrackA.id },
            { position: "track_b", spotify_track_id: spotifyTrackB.id },
          ],
        });
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
  }, [isAuthenticated, mode, trackA, trackB, spotifyTrackA, spotifyTrackB]);

  function handleSelectSpotifyTrack(track: SpotifySelectedTrack) {
    if (track.position === "track_a") {
      setSpotifyTrackA(track);
    } else {
      setSpotifyTrackB(track);
    }
  }

  function handleDeselectSpotifyTrack(position: "track_a" | "track_b") {
    if (position === "track_a") {
      setSpotifyTrackA(null);
    } else {
      setSpotifyTrackB(null);
    }
  }

  const canAnalyze =
    mode === "manual"
      ? !!trackA && !!trackB
      : !!spotifyTrackA && !!spotifyTrackB;

  const missingSelectionCopy = mode === "manual"
    ? !trackA && !trackB
      ? "Add Track A and Track B"
      : !trackA
        ? "Add Track A to continue"
        : "Add Track B to continue"
    : !spotifyTrackA && !spotifyTrackB
      ? "Select Track A and Track B"
      : !spotifyTrackA
        ? "Select Track A to continue"
        : "Select Track B to continue";

  return (
    <section className="mt-12 w-full">
      <AnimatePresence mode="wait">
        {status === "success" && result ? (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.5 }}
          >
            <Dashboard result={result} />
          </motion.div>
        ) : (
          <motion.div
            key="upload"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="rounded-3xl border border-zinc-800 bg-card/65 p-6 shadow-[0_25px_80px_-45px_rgba(0,0,0,1)] backdrop-blur md:p-8"
          >
            <div className="mb-8">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-secondary">
                How do you want to add your tracks?
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2" role="group" aria-label="Track source">
              <button
                type="button"
                onClick={() => setMode("manual")}
                aria-pressed={mode === "manual"}
                className={`flex items-center gap-4 rounded-2xl border p-4 text-left transition-all ${
                  mode === "manual"
                    ? "border-primary/50 bg-primary/10"
                    : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700"
                }`}
              >
                <FileAudio className={`h-6 w-6 ${mode === "manual" ? "text-primary" : "text-text-secondary"}`} />
                <span className="flex-1">
                  <span className="block text-sm font-semibold text-text">Upload audio files</span>
                  <span className="mt-1 block text-xs text-text-secondary">MP3, WAV, FLAC, AIFF and supported audio formats</span>
                </span>
                <ArrowRight className="h-4 w-4 text-text-tertiary" />
              </button>
              <button
                type="button"
                onClick={() => setMode("spotify")}
                aria-pressed={mode === "spotify"}
                className={`flex items-center gap-4 rounded-2xl border p-4 text-left transition-all ${
                  mode === "spotify"
                    ? "border-[#1DB954]/50 bg-[#1DB954]/10"
                    : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700"
                }`}
              >
                <Music className={`h-6 w-6 ${mode === "spotify" ? "text-[#1DB954]" : "text-text-secondary"}`} />
                <span className="flex-1">
                  <span className="block text-sm font-semibold text-text">Choose from Spotify</span>
                  <span className="mt-1 block text-xs text-text-secondary">Select two tracks without downloading MP3 files</span>
                </span>
                <ArrowRight className="h-4 w-4 text-text-tertiary" />
              </button>
              </div>
            </div>

            {mode === "manual" ? (
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
            ) : !isAuthenticated ? (
              <div className="rounded-2xl border border-[#1DB954]/20 bg-[#1DB954]/5 p-6 text-center">
                <Music className="mx-auto h-8 w-8 text-[#1DB954]" />
                <h2 className="mt-4 text-lg font-semibold text-text">Sign in to use Spotify</h2>
                <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-text-secondary">
                  Sign in, connect your Spotify account and choose two tracks directly from your library. Your destination will be preserved.
                </p>
              </div>
            ) : (
              <SpotifyAnalyzerSource
                selectedTrackA={spotifyTrackA}
                selectedTrackB={spotifyTrackB}
                onSelectTrack={handleSelectSpotifyTrack}
                onDeselectTrack={handleDeselectSpotifyTrack}
                onBack={() => setMode("manual")}
              />
            )}

            {isAuthenticated && !canAnalyze && !isBusy ? (
              <div className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-zinc-800/50 px-6 py-4 text-sm font-medium text-text-secondary/60">
                <Music className="h-4 w-4" />
                {missingSelectionCopy}
              </div>
            ) : (
              <button
                onClick={handleAnalyze}
                disabled={authLoading || isBusy}
                aria-busy={isBusy}
                className={`mt-6 flex w-full items-center justify-center gap-2 rounded-xl px-6 py-4 text-base font-bold transition-all ${
                  !isAuthenticated
                    ? "bg-primary/50 text-background hover:brightness-110"
                    : "bg-success text-black hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
                }`}
              >
                {!isAuthenticated ? (
                  <>Sign in to analyze</>
                ) : isBusy ? (
                  <>
                    <LoadingSpinner />
                    {STEPS[phase - 1]?.label ?? "Working..."}
                  </>
                ) : (
                  <>
                    <Upload className="h-5 w-5" />
                    {mode === "spotify" ? "Analyze selected tracks" : "Analyze uploaded tracks"}
                  </>
                )}
              </button>
            )}

            {isBusy && (
              <div className="mt-5 flex items-center justify-center gap-2">
                {STEPS.map((step, i) => {
                  const stepNum = i + 1;
                  const isActive = phase >= stepNum;
                  const isCurrent = phase === stepNum;
                  return (
                    <div key={step.key} className="flex items-center gap-2">
                      <div
                        className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-all duration-300 ${
                          isActive
                            ? "bg-success/15 text-success"
                            : "bg-zinc-800/50 text-text-secondary/50"
                        } ${isCurrent ? "ring-1 ring-success/30" : ""}`}
                      >
                        {isActive && stepNum < 4 ? (
                          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        ) : isActive && stepNum === 4 ? (
                          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <span className="h-3 w-3 rounded-full border border-current" />
                        )}
                        {step.label}
                      </div>
                      {i < STEPS.length - 1 && (
                        <div
                          className={`h-px w-4 transition-colors duration-300 ${
                            phase > stepNum ? "bg-success/40" : "bg-zinc-700/40"
                          }`}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {error ? (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 rounded-xl border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-200"
              >
                {error}
              </motion.p>
            ) : null}

            {!authLoading && !isAuthenticated && !error ? (
              <p role="alert" className="mt-4 rounded-xl border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-text-secondary">
                Sign in with Google or GitHub before running an analysis.
              </p>
            ) : null}
          </motion.div>
        )}
      </AnimatePresence>

      {status === "processing" && (
        <motion.div
          key="skeleton"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <SkeletonGrid />
        </motion.div>
      )}
      <AuthDialog open={authOpen} onOpenChange={setAuthOpen} returnTo="/analyzer" />
    </section>
  );
}
