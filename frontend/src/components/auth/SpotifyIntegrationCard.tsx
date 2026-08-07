"use client";

import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Music, Unlink, ExternalLink, Loader2, CheckCircle2, XCircle } from "lucide-react";

interface SpotifyStatus {
  connected: boolean;
  spotify_user_id?: string;
  display_name?: string;
  email?: string;
  scopes?: string[];
  connected_at?: string;
  needs_reauthorization?: boolean;
}

export function SpotifyIntegrationCard() {
  const [status, setStatus] = useState<SpotifyStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = useCallback(async (): Promise<SpotifyStatus | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/integrations/spotify?action=status", { cache: "no-store" });
      if (!response.ok) throw new Error("Failed to load status");
      const nextStatus = (await response.json()) as SpotifyStatus;
      setStatus(nextStatus);
      return nextStatus;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to load Spotify status");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const returnedFromSpotify = params.get("spotify") === "connected";
    let cancelled = false;

    const timer = window.setTimeout(() => {
      void (async () => {
        const nextStatus = await loadStatus();
        if (cancelled) return;

        if (
          returnedFromSpotify &&
          nextStatus?.connected &&
          !nextStatus.needs_reauthorization
        ) {
          window.location.replace("/analyzer?source=spotify");
          return;
        }

        if (returnedFromSpotify) {
          const url = new URL(window.location.href);
          url.searchParams.delete("spotify");
          window.history.replaceState({}, "", url.toString());
        }
      })();
    }, 0);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [loadStatus]);

  const handleConnect = useCallback(async () => {
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
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to disconnect Spotify");
    } finally {
      setDisconnecting(false);
    }
  }, []);

  const isConnected = status?.connected ?? false;
  const needsReauth = status?.needs_reauthorization ?? false;

  return (
    <div className="rounded-xl border border-border/50 bg-card/50 p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#1DB954]/10">
            <Music className="h-5 w-5 text-[#1DB954]" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text">Spotify</h3>
            <p className="text-sm text-text-secondary">
              {!isConnected && "Connect your Spotify account to import playlists and select tracks for analysis."}
              {isConnected && !needsReauth && "Connected"}
              {needsReauth && "Session expired — reconnect to continue using Spotify features."}
            </p>
          </div>
        </div>

        {loading ? (
          <Loader2 className="h-5 w-5 animate-spin text-text-tertiary" />
        ) : isConnected && !needsReauth ? (
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 text-xs text-green-400">
              <CheckCircle2 className="h-3.5 w-3.5" /> Connected
            </span>
          </div>
        ) : needsReauth ? (
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 text-xs text-amber-400">
              <XCircle className="h-3.5 w-3.5" /> Reconnect required
            </span>
          </div>
        ) : null}
      </div>

      {!loading && isConnected && !needsReauth && status && (
        <div className="mt-4 space-y-1 rounded-lg bg-background/50 px-4 py-3 text-sm">
          {status.display_name && (
            <p className="text-text"><span className="text-text-secondary">Name:</span> {status.display_name}</p>
          )}
          {status.email && (
            <p className="text-text"><span className="text-text-secondary">Email:</span> {status.email}</p>
          )}
          {status.scopes && status.scopes.length > 0 && (
            <p className="text-text-secondary text-xs">
              Scopes: {status.scopes.join(", ")}
            </p>
          )}
        </div>
      )}

      {error && (
        <div className="mt-4 flex items-center gap-2 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-200">
          <XCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="mt-4 flex gap-3">
        {!loading && (!isConnected || needsReauth) && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleConnect}
            disabled={connecting}
            className="inline-flex items-center gap-2 rounded-lg bg-[#1DB954] px-4 py-2 text-sm font-medium text-black transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {connecting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ExternalLink className="h-4 w-4" />
            )}
            {connecting ? "Connecting to Spotify…" : needsReauth ? "Reconnect Spotify" : "Connect Spotify"}
          </motion.button>
        )}

        {!loading && isConnected && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleDisconnect}
            disabled={disconnecting}
            className="inline-flex items-center gap-2 rounded-lg border border-danger/40 px-4 py-2 text-sm font-medium text-danger transition-colors hover:bg-danger/10 disabled:opacity-50"
          >
            {disconnecting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Unlink className="h-4 w-4" />
            )}
            {disconnecting ? "Disconnecting…" : "Disconnect"}
          </motion.button>
        )}
      </div>
    </div>
  );
}
