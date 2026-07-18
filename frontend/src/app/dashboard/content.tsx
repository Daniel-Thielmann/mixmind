"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { BarChart3, Music, Activity, Sparkles, RefreshCw } from "lucide-react";

interface RecentTrack {
  id: string;
  filename: string;
  bpm: number | null;
  camelot: string | null;
  energy: number | null;
}

interface DashboardSummary {
  tracks_count: number;
  analyses_count: number;
  recent_tracks: RecentTrack[];
}

export function DashboardContent() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/dashboard", { cache: "no-store" });
      if (!response.ok) {
        const payload = (await response.json().catch(() => null)) as
          | { detail?: string }
          | null;
        throw new Error(payload?.detail ?? "Unable to load your dashboard.");
      }
      setSummary((await response.json()) as DashboardSummary);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load your dashboard.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  return (
    <div className="flex-1 pb-12 pt-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-linear-to-br from-primary to-primary-dark text-background shadow-lg shadow-primary/20">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-text">
              Welcome back, {user?.name?.split(" ")[0] ?? "DJ"}
            </h1>
            <p className="mt-1 text-text-secondary">Your persisted MixMind activity.</p>
          </div>
        </div>

        {loading && <DashboardSkeleton />}

        {!loading && error && (
          <div className="mt-8 rounded-xl border border-danger/40 bg-danger/10 p-6 text-sm text-red-200">
            <p>{error}</p>
            <button type="button" onClick={() => void load()} className="mt-4 inline-flex items-center gap-2 rounded-lg border border-danger/40 px-3 py-2">
              <RefreshCw className="h-4 w-4" /> Try again
            </button>
          </div>
        )}

        {!loading && !error && summary && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <StatCard label="Analyses" value={summary.analyses_count} icon={BarChart3} />
              <StatCard label="Tracks" value={summary.tracks_count} icon={Music} />
            </div>

            <section className="mt-12 rounded-xl border border-border/50 bg-card/50 p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-text">Recent tracks</h2>
                <Activity className="h-4 w-4 text-text-tertiary" />
              </div>
              {summary.recent_tracks.length === 0 ? (
                <div className="py-12 text-center">
                  <p className="text-sm text-text-secondary">No tracks yet.</p>
                  <a href="/analyzer" className="mt-4 inline-block rounded-lg bg-primary px-4 py-2 text-sm font-medium text-background">Analyze your first tracks</a>
                </div>
              ) : (
                <div className="mt-4 space-y-3">
                  {summary.recent_tracks.map((track) => (
                    <div key={track.id} className="flex items-center justify-between rounded-lg border border-border/30 bg-background/50 px-4 py-3">
                      <span className="truncate text-sm font-medium text-text">{track.filename}</span>
                      <div className="flex gap-3 text-xs text-text-secondary">
                        <span>{track.bpm == null ? "—" : `${track.bpm.toFixed(1)} BPM`}</span>
                        <span className="text-primary">{track.camelot ?? "—"}</span>
                        <span>{track.energy == null ? "—" : `${Math.round(track.energy * 100)}%`}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </motion.div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon }: { label: string; value: number; icon: typeof Music }) {
  return (
    <div className="rounded-xl border border-border/50 bg-card/50 p-5">
      <div className="flex items-center justify-between text-sm text-text-secondary"><span>{label}</span><Icon className="h-4 w-4" /></div>
      <p className="mt-2 text-2xl font-semibold text-text">{value}</p>
    </div>
  );
}

function DashboardSkeleton() {
  return <div className="mt-8 grid animate-pulse gap-4 sm:grid-cols-2"><div className="h-28 rounded-xl bg-card" /><div className="h-28 rounded-xl bg-card" /></div>;
}
