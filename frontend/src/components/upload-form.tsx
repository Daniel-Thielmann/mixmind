"use client";

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, CirclePlay as Youtube, FileAudio, LockKeyhole, Music, Upload } from "lucide-react";

import { AuthDialog } from "@/components/auth/AuthDialog";
import { Dashboard } from "@/components/home/dashboard";
import { SpotifyAnalyzerSource } from "@/components/spotify/SpotifyAnalyzerSource";
import { YouTubeAnalyzerSource } from "@/components/youtube/YouTubeAnalyzerSource";
import { UploadCard } from "@/components/upload/upload-card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { SkeletonGrid } from "@/components/ui/Skeleton";
import { loadSpotifyTracks, clearSpotifyTracks } from "@/lib/spotify-storage";
import { apiService } from "@/services/api";
import { analyzeSpotifyTracks } from "@/services/spotify-service";
import { youtubeService } from "@/services/youtube-service";
import { useAuth } from "@/hooks/useAuth";
import type {
  AudioAnalysis,
  AnalysisProgressEvent,
  CompatibilityResult,
  UploadAnalysisResponse,
  UploadStatus,
} from "@/types";
import type { SpotifySelectedTrack } from "@/types/spotify";
import type { YouTubeTrack } from "@/types/youtube-track";

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

type InputMode = "manual" | "spotify" | "youtube";

export function UploadForm() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [mode, setMode] = useState<InputMode>("youtube");

  const [trackA, setTrackA] = useState<File>();
  const [trackB, setTrackB] = useState<File>();

  const [spotifyTrackA, setSpotifyTrackA] = useState<SpotifySelectedTrack | null>(null);
  const [spotifyTrackB, setSpotifyTrackB] = useState<SpotifySelectedTrack | null>(null);
  const [youtubeTrackA, setYoutubeTrackA] = useState<YouTubeTrack | null>(null);
  const [youtubeTrackB, setYoutubeTrackB] = useState<YouTubeTrack | null>(null);

  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadAnalysisResponse | null>(null);
  const [showAiPhase, setShowAiPhase] = useState(false);
  const [progressEvent, setProgressEvent] =
    useState<AnalysisProgressEvent | null>(null);
  const [partialResult, setPartialResult] = useState<{
    trackA?: AudioAnalysis;
    trackB?: AudioAnalysis;
    compatibility?: CompatibilityResult;
  }>({});
  const [authOpen, setAuthOpen] = useState(false);

  const isBusy = status === "uploading" || status === "processing";

  const handleProgress = useCallback((event: AnalysisProgressEvent) => {
    setProgressEvent(event);
    if (event.stage === "track_a_analyzed") {
      setPartialResult((current) => ({
        ...current,
        trackA: event.data as AudioAnalysis,
      }));
    } else if (event.stage === "track_b_analyzed") {
      setPartialResult((current) => ({
        ...current,
        trackB: event.data as AudioAnalysis,
      }));
    } else if (event.stage === "compatibility_computed") {
      setPartialResult((current) => ({
        ...current,
        compatibility: event.data as CompatibilityResult,
      }));
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams(window.location.search);
      if (params.get("source") === "spotify") setMode("spotify");
      if (params.get("source") === "youtube") setMode("youtube");
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
  else if (status === "processing") {
    if (progressEvent) {
      if (progressEvent.stage === "acquiring_tracks") phase = 1;
      else if (progressEvent.stage === "ai_recommendation_started") phase = 3;
      else phase = 2;
    } else {
      phase = showAiPhase ? 3 : 2;
    }
  }
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
      setProgressEvent(null);
      setPartialResult({});
      await new Promise<void>((resolve) => {
        window.setTimeout(resolve, 0);
      });
      try {
        setStatus("processing");
        const response = await apiService.analyzeTracks(
          trackA,
          trackB,
          handleProgress,
        );
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
    } else if (mode === "spotify") {
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
    } else {
      if (!youtubeTrackA || !youtubeTrackB) { setResult(null); setStatus("error"); setError(FRIENDLY_VALIDATION_MESSAGE); return; }
      setStatus("uploading"); setError(null); setResult(null);
      await new Promise<void>((resolve) => window.setTimeout(resolve, 0));
      try { setStatus("processing"); setProgressEvent(null); setPartialResult({}); setResult(await youtubeService.analyze(youtubeTrackA, youtubeTrackB, handleProgress)); setStatus("success"); }
      catch (requestError) { setResult(null); setStatus("error"); setError(requestError instanceof Error ? requestError.message : FRIENDLY_ERROR_MESSAGE); }
    }
  }, [isAuthenticated, mode, trackA, trackB, spotifyTrackA, spotifyTrackB, youtubeTrackA, youtubeTrackB, handleProgress]);

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
      : mode === "spotify" ? false : !!youtubeTrackA && !!youtubeTrackB;

  const missingSelectionCopy = mode === "manual"
    ? !trackA && !trackB
      ? "Add Track A and Track B"
      : !trackA
        ? "Add Track A to continue"
        : "Add Track B to continue"
    : mode === "spotify"
      ? "Spotify integration requires Pro"
      : !youtubeTrackA && !youtubeTrackB ? "Select Track A and Track B" : !youtubeTrackA ? "Select Track A to continue" : "Select Track B to continue";

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
              <div className="mt-4 grid gap-3 md:grid-cols-3" role="group" aria-label="Track source">
              <button
                type="button"
                onClick={() => setMode("youtube")}
                aria-pressed={mode === "youtube"}
                className={`flex items-center gap-4 rounded-2xl border p-4 text-left transition-all ${mode === "youtube" ? "border-red-500/50 bg-red-500/10" : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700"}`}
              >
                <Youtube className={`h-6 w-6 ${mode === "youtube" ? "text-red-500" : "text-text-secondary"}`} />
                <span className="flex-1"><span className="block text-sm font-semibold text-text">Choose from YouTube</span><span className="mt-1 block text-xs text-text-secondary">Search the music catalog</span></span>
                <ArrowRight className="h-4 w-4 text-text-tertiary" />
              </button>
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
                  <span className="flex items-center gap-2 text-sm font-semibold text-text">Choose from Spotify <span className="rounded-full bg-amber-300/10 px-2 py-0.5 text-[9px] font-bold uppercase text-amber-200">Pro</span></span>
                  <span className="mt-1 block text-xs text-text-secondary">Available to approved Pro accounts</span>
                </span>
                <LockKeyhole className="h-4 w-4 text-amber-200" />
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
              <div className={`rounded-2xl border p-6 text-center ${mode === "youtube" ? "border-red-500/20 bg-red-500/5" : "border-[#1DB954]/20 bg-[#1DB954]/5"}`}>
                {mode === "youtube" ? <Youtube className="mx-auto h-8 w-8 text-red-500" /> : <Music className="mx-auto h-8 w-8 text-[#1DB954]" />}
                <h2 className="mt-4 text-lg font-semibold text-text">Sign in to use {mode === "spotify" ? "Spotify" : "YouTube"}</h2>
                <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-text-secondary">
                  {mode === "youtube" ? "Sign in to search YouTube and select two tracks for analysis. Your destination will be preserved." : "Spotify access is available to approved Pro accounts."}
                </p>
              </div>
            ) : mode === "spotify" ? (
              <SpotifyAnalyzerSource
                selectedTrackA={spotifyTrackA}
                selectedTrackB={spotifyTrackB}
                onSelectTrack={handleSelectSpotifyTrack}
                onDeselectTrack={handleDeselectSpotifyTrack}
                onBack={() => setMode("manual")}
              />
            ) : (
              <YouTubeAnalyzerSource selectedTrackA={youtubeTrackA} selectedTrackB={youtubeTrackB} onSelect={(track, position) => position === "track_a" ? setYoutubeTrackA(track) : setYoutubeTrackB(track)} onDeselect={(position) => position === "track_a" ? setYoutubeTrackA(null) : setYoutubeTrackB(null)} />
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
                    {progressEvent?.message ?? STEPS[phase - 1]?.label ?? "Working..."}
                  </>
                ) : (
                  <>
                    <Upload className="h-5 w-5" />
                    {mode === "manual" ? "Analyze uploaded tracks" : "Analyze selected tracks"}
                  </>
                )}
              </button>
            )}

            {isBusy && (
              <div className="mt-5">
                {progressEvent ? (
                  <div className="mb-3 flex items-center justify-between text-xs text-text-secondary">
                    <span>{progressEvent.message}</span>
                    <span>{progressEvent.progress}%</span>
                  </div>
                ) : null}
                <div className="flex items-center justify-center gap-2">
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
                {partialResult.trackA || partialResult.trackB ? (
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    {[
                      ["Track A", partialResult.trackA],
                      ["Track B", partialResult.trackB],
                    ].map(([label, track]) =>
                      track && typeof track !== "string" ? (
                        <div key={label as string} className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-3 text-sm">
                          <p className="font-semibold text-text">{label as string}</p>
                          <p className="mt-1 text-text-secondary">
                            {track.bpm.toFixed(1)} BPM · {track.camelot ?? track.key ?? "Unknown"} · energy {track.energy.toFixed(3)}
                          </p>
                        </div>
                      ) : null,
                    )}
                  </div>
                ) : null}
                {partialResult.compatibility ? (
                  <div className="mt-3 rounded-xl border border-success/20 bg-success/5 p-3 text-sm text-text-secondary">
                    Compatibility ready: <span className="font-semibold text-success">{partialResult.compatibility.compatibility_score.toFixed(0)}/100</span>
                  </div>
                ) : null}
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
