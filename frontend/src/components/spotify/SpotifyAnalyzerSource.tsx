"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AlertCircle, ExternalLink, Loader2, Music } from "lucide-react";

import { SpotifySelector } from "@/components/spotify/SpotifySelector";
import type { SpotifySelectedTrack } from "@/types/spotify";

interface SpotifyStatus {
  connected: boolean;
  spotify_user_id?: string;
  display_name?: string;
  needs_reauthorization?: boolean;
}

interface SpotifyAnalyzerSourceProps {
  selectedTrackA: SpotifySelectedTrack | null;
  selectedTrackB: SpotifySelectedTrack | null;
  onSelectTrack: (track: SpotifySelectedTrack) => void;
  onDeselectTrack: (position: "track_a" | "track_b") => void;
  onBack: () => void;
}

export function SpotifyAnalyzerSource({
  selectedTrackA,
  selectedTrackB,
  onSelectTrack,
  onDeselectTrack,
  onBack,
}: SpotifyAnalyzerSourceProps) {
  const [status, setStatus] = useState<SpotifyStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/integrations/spotify?action=status", {
        cache: "no-store",
      });
      if (!response.ok) throw new Error("Unable to check your Spotify connection.");
      setStatus((await response.json()) as SpotifyStatus);
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Unable to check your Spotify connection.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void loadStatus(), 0);
    return () => window.clearTimeout(timer);
  }, [loadStatus]);

  const connect = useCallback(async () => {
    setConnecting(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        action: "connect",
        return_to: "/analyzer?source=spotify",
      });
      const response = await fetch(`/api/integrations/spotify?${params}`, {
        cache: "no-store",
      });
      const body = (await response.json().catch(() => null)) as
        | { authorization_url?: string; detail?: string }
        | null;
      if (!response.ok || !body?.authorization_url) {
        throw new Error(body?.detail ?? "Unable to connect Spotify.");
      }
      window.location.assign(body.authorization_url);
    } catch (cause) {
      setConnecting(false);
      setError(cause instanceof Error ? cause.message : "Unable to connect Spotify.");
    }
  }, []);

  if (loading) {
    return (
      <div role="status" className="flex min-h-52 items-center justify-center gap-2 text-sm text-text-secondary">
        <Loader2 className="h-5 w-5 animate-spin" /> Checking Spotify connection…
      </div>
    );
  }

  const needsConnection =
    !status?.connected || status.needs_reauthorization === true;

  if (needsConnection) {
    return (
      <div className="rounded-2xl border border-[#1DB954]/20 bg-[#1DB954]/5 p-6 md:p-8">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[#1DB954]/15">
            <Music className="h-6 w-6 text-[#1DB954]" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-text">Connect Spotify</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-text-secondary">
              Connect your Spotify account and choose two tracks directly from
              your playlists or saved music. No MP3 download or manual upload is
              required.
            </p>
          </div>
        </div>

        {error && (
          <p role="alert" className="mt-5 flex items-center gap-2 text-sm text-red-300">
            <AlertCircle className="h-4 w-4" /> {error}
          </p>
        )}

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => void connect()}
            disabled={connecting}
            className="inline-flex items-center gap-2 rounded-xl bg-[#1DB954] px-5 py-3 text-sm font-semibold text-black hover:brightness-105 disabled:opacity-50"
          >
            {connecting ? <Loader2 className="h-4 w-4 animate-spin" /> : <ExternalLink className="h-4 w-4" />}
            {connecting ? "Opening Spotify…" : status?.needs_reauthorization ? "Reconnect Spotify" : "Connect Spotify"}
          </button>
          <button type="button" onClick={onBack} className="rounded-xl border border-border px-5 py-3 text-sm text-text-secondary hover:text-text">
            Use audio files instead
          </button>
          <Link href="/dashboard/settings/integrations" className="inline-flex items-center px-2 text-sm text-text-secondary underline underline-offset-4 hover:text-text">
            Manage integration
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#1DB954]/15 bg-[#1DB954]/5 px-4 py-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="h-2 w-2 rounded-full bg-[#1DB954]" aria-hidden="true" />
          <span className="font-medium text-text">{status.display_name ?? "Spotify connected"}</span>
        </div>
        <Link href="/dashboard/settings/integrations" className="text-xs text-text-secondary underline underline-offset-4 hover:text-text">
          Manage integration
        </Link>
      </div>
      <SpotifySelector
        spotifyUserId={status.spotify_user_id ?? null}
        selectedTrackA={selectedTrackA}
        selectedTrackB={selectedTrackB}
        onSelectTrack={onSelectTrack}
        onDeselectTrack={onDeselectTrack}
        onBack={onBack}
      />
    </div>
  );
}
