"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, Loader2, Music, Settings } from "lucide-react";

interface SpotifyStatus {
  connected: boolean;
  needs_reauthorization?: boolean;
}

export function SpotifyStatusSummary() {
  const [status, setStatus] = useState<SpotifyStatus | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      try {
        const response = await fetch("/api/integrations/spotify?action=status", {
          cache: "no-store",
          signal: controller.signal,
        });
        if (response.ok) setStatus((await response.json()) as SpotifyStatus);
        else setStatus({ connected: false });
      } catch {
        if (!controller.signal.aborted) setStatus({ connected: false });
      }
    }, 0);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, []);

  const connected = status?.connected && !status.needs_reauthorization;

  return (
    <section className="rounded-xl border border-border/50 bg-card/50 p-5" aria-labelledby="integration-status-title">
      <div className="flex items-start justify-between gap-4">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#1DB954]/10">
            <Music className="h-5 w-5 text-[#1DB954]" />
          </div>
          <div>
            <h2 id="integration-status-title" className="font-semibold text-text">Spotify integration</h2>
            {status === null ? (
              <p role="status" className="mt-1 flex items-center gap-2 text-sm text-text-secondary">
                <Loader2 className="h-3.5 w-3.5 animate-spin" /> Checking status…
              </p>
            ) : (
              <p className="mt-1 flex items-center gap-2 text-sm text-text-secondary">
                {connected && <CheckCircle2 className="h-3.5 w-3.5 text-[#1DB954]" />}
                {connected ? "Connected and ready in Analyzer" : status.needs_reauthorization ? "Reconnect required" : "Not connected"}
              </p>
            )}
          </div>
        </div>
        <Link href="/dashboard/settings/integrations" className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs text-text-secondary hover:text-text">
          <Settings className="h-3.5 w-3.5" /> Manage
        </Link>
      </div>
    </section>
  );
}
