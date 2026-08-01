"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Loader2,
  Music,
  RefreshCw,
  Sparkles,
  Unlink,
  User,
} from "lucide-react";

import { SpotifySelector } from "@/components/spotify/SpotifySelector";
import { saveSpotifyTracks } from "@/lib/spotify-storage";
import type { SpotifySelectedTrack } from "@/types/spotify";

interface SpotifyStatus {
  connected: boolean;
  spotify_user_id?: string;
  display_name?: string;
  email?: string;
  scopes?: string[];
  connected_at?: string;
  needs_reauthorization?: boolean;
}

export function SpotifyLibrary() {
  const router = useRouter();
  const [status, setStatus] = useState<SpotifyStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [callbackMessage, setCallbackMessage] = useState<string | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [navigating, setNavigating] = useState(false);

  const [spotifyTrackA, setSpotifyTrackA] = useState<SpotifySelectedTrack | null>(null);
  const [spotifyTrackB, setSpotifyTrackB] = useState<SpotifySelectedTrack | null>(null);

  const loadStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/integrations/spotify?action=status", { cache: "no-store" });
      if (!response.ok) throw new Error("Failed to load status");
      setStatus((await response.json()) as SpotifyStatus);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to load Spotify status");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    let nextCallbackMessage: string | null = null;
    if (params.get("spotify") === "connected") {
      nextCallbackMessage = "Spotify connected successfully.";
      const url = new URL(window.location.href);
      url.searchParams.delete("spotify");
      window.history.replaceState({}, "", url.toString());
    } else if (params.get("spotify") === "error") {
      const msg = params.get("message") ?? "unknown";
      const friendly = msg === "access_denied"
        ? "Spotify authorization was denied."
        : msg === "missing_state"
          ? "Connection failed. Please try again."
          : `Connection failed: ${msg.replace(/_/g, " ")}`;
      nextCallbackMessage = friendly;
      const url = new URL(window.location.href);
      url.searchParams.delete("spotify");
      url.searchParams.delete("message");
      window.history.replaceState({}, "", url.toString());
    }
    const timer = window.setTimeout(() => {
      if (nextCallbackMessage) setCallbackMessage(nextCallbackMessage);
      void loadStatus();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadStatus]);

  useEffect(() => {
    if (!callbackMessage) return;
    const timer = window.setTimeout(() => setCallbackMessage(null), 6000);
    return () => window.clearTimeout(timer);
  }, [callbackMessage]);

  const handleConnect = useCallback(async () => {
    setConnecting(true);
    setError(null);
    try {
      const response = await fetch("/api/integrations/spotify?action=connect", { cache: "no-store" });
      if (!response.ok) throw new Error("Failed to start connection");
      const data = (await response.json()) as { authorization_url?: string };
      if (data.authorization_url) {
        window.location.href = data.authorization_url;
      } else {
        throw new Error("No authorization URL returned");
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to connect Spotify");
      setConnecting(false);
    }
  }, []);

  const handleDisconnect = useCallback(async () => {
    if (!window.confirm("Disconnect Spotify? Your MixMind account and data will not be affected.")) return;
    setDisconnecting(true);
    setError(null);
    try {
      const response = await fetch("/api/integrations/spotify", { method: "DELETE" });
      if (response.status !== 204) throw new Error("Failed to disconnect");
      setStatus({ connected: false });
      setSpotifyTrackA(null);
      setSpotifyTrackB(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to disconnect Spotify");
    } finally {
      setDisconnecting(false);
    }
  }, []);

  const handleSelectTrack = useCallback((track: SpotifySelectedTrack) => {
    if (track.id === spotifyTrackA?.id) {
      setSpotifyTrackA(null);
      return;
    }
    if (track.id === spotifyTrackB?.id) {
      setSpotifyTrackB(null);
      return;
    }
    if (!spotifyTrackA) {
      setSpotifyTrackA({ ...track, position: "track_a" });
    } else if (!spotifyTrackB) {
      setSpotifyTrackB({ ...track, position: "track_b" });
    }
  }, [spotifyTrackA, spotifyTrackB]);

  const handleDeselectTrack = useCallback((position: "track_a" | "track_b") => {
    if (position === "track_a") setSpotifyTrackA(null);
    else setSpotifyTrackB(null);
  }, []);

  const canAnalyze = spotifyTrackA !== null && spotifyTrackB !== null;
  const isConnected = status?.connected ?? false;
  const needsReauth = status?.needs_reauthorization ?? false;

  const handleAnalyze = useCallback(() => {
    if (!canAnalyze || navigating) return;
    setNavigating(true);
    const saved = saveSpotifyTracks(spotifyTrackA!, spotifyTrackB!);
    if (!saved) {
      setNavigating(false);
      return;
    }
    router.push("/analyzer?spotify=1");
  }, [canAnalyze, navigating, spotifyTrackA, spotifyTrackB, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-danger/30 bg-danger/5 p-6 text-center">
        <p className="text-sm text-red-200">{error}</p>
        <button
          type="button"
          onClick={() => void loadStatus()}
          className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-danger/15 px-3 py-1.5 text-xs font-medium text-danger hover:bg-danger/25"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </div>
    );
  }

  if (!isConnected || needsReauth) {
    return (
      <div className="overflow-hidden rounded-xl border border-border/50 bg-card/50 backdrop-blur-sm">
        <div className="p-6 md:p-8">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#1DB954]/10">
              <Music className="h-7 w-7 text-[#1DB954]" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-text">
                Analyze tracks directly from Spotify
              </h3>
              <p className="mt-1 text-sm text-text-secondary">
                Connect your Spotify account and choose two tracks directly from your playlists or liked songs. No MP3 downloads and no manual uploads required.
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {[
              "No need to download MP3 files",
              "Browse your playlists and liked songs",
              "Select Track A and Track B directly",
              "MixMind handles the analysis automatically",
            ].map((benefit) => (
              <div key={benefit} className="flex items-center gap-2 text-sm text-text-secondary">
                <svg className="h-4 w-4 shrink-0 text-[#1DB954]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {benefit}
              </div>
            ))}
          </div>

          {callbackMessage && (
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{callbackMessage}</span>
            </div>
          )}

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleConnect}
              disabled={connecting}
              className="inline-flex items-center gap-2 rounded-xl bg-[#1DB954] px-6 py-3 font-semibold text-black transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {connecting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Music className="h-4 w-4" />
              )}
              {connecting ? "Connecting to Spotify\u2026" : needsReauth ? "Reconnect Spotify" : "Connect Spotify"}
            </motion.button>

            <a
              href="/analyzer"
              className="inline-flex items-center gap-2 rounded-xl border border-border/40 px-6 py-3 text-sm font-medium text-text-secondary transition-colors hover:border-text-secondary/30 hover:text-text"
            >
              <ArrowRight className="h-4 w-4" />
              Upload two audio files manually
            </a>
          </div>
        </div>

        {needsReauth && (
          <div className="border-t border-border/30 bg-amber-500/5 px-6 py-3">
            <p className="text-xs text-amber-400">
              Your Spotify connection has expired. Reconnect to continue.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border/50 bg-card/50 backdrop-blur-sm">
      {callbackMessage && (
        <div className="flex items-center gap-2 border-b border-border/30 bg-[#1DB954]/5 px-6 py-3 text-sm text-[#1DB954]">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{callbackMessage}</span>
        </div>
      )}

      <div className="border-b border-border/30 p-4 md:p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#1DB954]/10">
              <User className="h-5 w-5 text-[#1DB954]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-text">
                  {status?.display_name ?? "Your Spotify Library"}
                </h3>
                <span className="flex items-center gap-1 rounded-full bg-[#1DB954]/10 px-2 py-0.5 text-xs font-medium text-[#1DB954]">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#1DB954]" />
                  Connected
                </span>
              </div>
              <p className="text-xs text-text-secondary">
                Choose tracks from Spotify
              </p>
            </div>
          </div>
          <button
            onClick={handleDisconnect}
            disabled={disconnecting}
            className="inline-flex items-center gap-1.5 rounded-lg border border-danger/30 px-3 py-1.5 text-xs font-medium text-danger transition-colors hover:bg-danger/10 disabled:opacity-50"
          >
            {disconnecting ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <Unlink className="h-3 w-3" />
            )}
            {disconnecting ? "Disconnecting\u2026" : "Manage integration"}
          </button>
        </div>
      </div>

      <div className="p-4 md:p-6">
        <SpotifySelector
          spotifyUserId={status?.spotify_user_id ?? null}
          selectedTrackA={spotifyTrackA}
          selectedTrackB={spotifyTrackB}
          onSelectTrack={handleSelectTrack}
          onDeselectTrack={handleDeselectTrack}
          onBack={() => {}}
        />

        <div className="mt-4">
          <button
            onClick={handleAnalyze}
            disabled={!canAnalyze || navigating}
            aria-disabled={!canAnalyze || navigating}
            className={`flex w-full items-center justify-center gap-2 rounded-xl px-6 py-4 text-base font-bold transition-all focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
              canAnalyze && !navigating
                ? "bg-primary text-background shadow-lg shadow-primary/15 hover:brightness-110"
                : "cursor-not-allowed bg-zinc-800/50 text-text-secondary/50"
            }`}
          >
            {navigating ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : canAnalyze ? (
              <Sparkles className="h-5 w-5" />
            ) : (
              <Music className="h-5 w-5" />
            )}
            {navigating
              ? "Opening Analyzer\u2026"
              : canAnalyze
                ? "Analyze selected tracks"
                : !spotifyTrackA && !spotifyTrackB
                  ? "Select Track A and Track B"
                  : !spotifyTrackA
                    ? "Select Track A to continue"
                    : "Select Track B to continue"
            }
          </button>
        </div>
      </div>
    </div>
  );
}
