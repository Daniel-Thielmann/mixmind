"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload } from "lucide-react";

import { AuthDialog } from "@/components/auth/AuthDialog";
import { Dashboard } from "@/components/home/dashboard";
import { UploadCard } from "@/components/upload/upload-card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { SkeletonGrid } from "@/components/ui/Skeleton";
import { apiService } from "@/services/api";
import { useAuth } from "@/hooks/useAuth";
import type { UploadAnalysisResponse, UploadStatus } from "@/types";

const FRIENDLY_VALIDATION_MESSAGE =
  "Please select both tracks before analyzing.";
const FRIENDLY_ERROR_MESSAGE =
  "Unable to analyze the selected tracks. Please try again.";

const STEPS = [
  { key: "upload", label: "Uploading tracks" },
  { key: "process", label: "Processing audio" },
  { key: "ai", label: "AI generating recommendation" },
  { key: "done", label: "Complete" },
] as const;

export function UploadForm() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [trackA, setTrackA] = useState<File>();
  const [trackB, setTrackB] = useState<File>();
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadAnalysisResponse | null>(null);
  const [showAiPhase, setShowAiPhase] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);

  const isBusy = status === "uploading" || status === "processing";

  useEffect(() => {
    if (status !== "processing") return;
    const t = setTimeout(() => setShowAiPhase(true), 3000);
    return () => clearTimeout(t);
  }, [status]);

  let phase = 0;
  if (status === "uploading") phase = 1;
  else if (status === "processing") phase = showAiPhase ? 3 : 2;
  else if (status === "success") phase = 4;

  async function handleAnalyze() {
    if (!isAuthenticated) {
      setResult(null);
      setStatus("error");
      setError("You need to sign in before running an analysis.");
      setAuthOpen(true);
      return;
    }

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
              disabled={authLoading || (isAuthenticated && (!trackA || !trackB || isBusy))}
              aria-busy={isBusy}
              className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-success px-6 py-4 text-base font-bold text-black transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-55"
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
                  Analyze Tracks
                </>
              )}
            </button>

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

      {/* Skeleton loading while processing */}
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
      <AuthDialog open={authOpen} onOpenChange={setAuthOpen} />
    </section>
  );
}
