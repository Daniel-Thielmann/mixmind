"use client";

import { useState } from "react";
import { CirclePlay, Loader2, Search, X } from "lucide-react";

import { youtubeService } from "@/services/youtube-service";
import type { YouTubeTrack } from "@/types/youtube-track";

type Position = "track_a" | "track_b";

interface Props {
  selectedTrackA: YouTubeTrack | null;
  selectedTrackB: YouTubeTrack | null;
  onSelect: (track: YouTubeTrack, position: Position) => void;
  onDeselect: (position: Position) => void;
}

function SelectionCard({ label, track, accent, onRemove }: { label: string; track: YouTubeTrack | null; accent: string; onRemove: () => void }) {
  return (
    <div className={`min-w-0 rounded-xl border p-3 ${track ? accent : "border-dashed border-zinc-700 bg-zinc-900/30"}`}>
      <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] text-text-secondary">{label}</p>
      {track ? (
        <div className="flex items-center gap-3">
          <div className="h-12 w-20 shrink-0 rounded-md bg-zinc-800 bg-cover bg-center" style={track.thumbnail ? { backgroundImage: `url(${track.thumbnail})` } : undefined} />
          <div className="min-w-0 flex-1"><strong className="block truncate text-sm text-text">{track.title}</strong><span className="block truncate text-xs text-text-secondary">{track.channel}</span></div>
          <button type="button" onClick={onRemove} aria-label={`Remove ${label}`} className="rounded-lg p-2 text-text-secondary hover:bg-white/5 hover:text-text"><X className="h-4 w-4" /></button>
        </div>
      ) : <p className="py-3 text-sm text-text-secondary">Choose a track from the search results.</p>}
    </div>
  );
}

export function YouTubeAnalyzerSource({ selectedTrackA, selectedTrackB, onSelect, onDeselect }: Props) {
  const [query, setQuery] = useState("");
  const [tracks, setTracks] = useState<YouTubeTrack[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function search() {
    if (!query.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      setTracks((await youtubeService.search(query.trim())).items);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "YouTube search failed.");
    } finally {
      setLoading(false);
    }
  }

  return <div className="space-y-5">
    <div className="grid gap-3 md:grid-cols-2" aria-label="Selected YouTube tracks">
      <SelectionCard label="Track A" track={selectedTrackA} accent="border-cyan-400/40 bg-cyan-400/5" onRemove={() => onDeselect("track_a")} />
      <SelectionCard label="Track B" track={selectedTrackB} accent="border-fuchsia-400/40 bg-fuchsia-400/5" onRemove={() => onDeselect("track_b")} />
    </div>
    <div className="flex gap-2">
      <div className="relative min-w-0 flex-1"><Search className="absolute left-4 top-3.5 h-4 w-4 text-text-secondary" /><input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void search(); }} placeholder="Search music on YouTube" aria-label="Search music on YouTube" className="w-full rounded-xl border border-zinc-700 bg-zinc-900 py-3 pl-11 pr-4 text-sm text-text outline-none focus:border-red-500" /></div>
      <button type="button" onClick={() => void search()} disabled={!query.trim() || loading} className="rounded-xl bg-red-600 px-5 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50">Search</button>
    </div>
    {loading && <div role="status" className="flex justify-center p-6"><Loader2 className="h-5 w-5 animate-spin text-red-500" /><span className="sr-only">Searching YouTube</span></div>}
    {!loading && tracks.length > 0 && <div className="max-h-[34rem] space-y-2 overflow-y-auto">{tracks.map((track) => { const a = selectedTrackA?.id === track.id; const b = selectedTrackB?.id === track.id; return <div key={track.id} className="flex flex-col gap-3 rounded-xl border border-zinc-800 bg-zinc-900/50 p-3 sm:flex-row sm:items-center"><div className="flex h-12 w-20 shrink-0 items-center justify-center rounded bg-zinc-800 bg-cover bg-center" style={track.thumbnail ? { backgroundImage: `url(${track.thumbnail})` } : undefined}>{!track.thumbnail && <CirclePlay className="h-8 w-8 text-red-500" />}</div><div className="min-w-0 flex-1"><strong className="block truncate text-sm text-text">{track.title}</strong><span className="block truncate text-xs text-text-secondary">{track.channel}</span></div><div className="flex gap-2"><button type="button" disabled={b} onClick={() => a ? onDeselect("track_a") : onSelect(track, "track_a")} className={`rounded-lg border px-3 py-1.5 text-xs disabled:cursor-not-allowed disabled:opacity-35 ${a ? "border-cyan-400 bg-cyan-400/15" : "border-zinc-700"}`}>{a ? "Selected A" : "Track A"}</button><button type="button" disabled={a} onClick={() => b ? onDeselect("track_b") : onSelect(track, "track_b")} className={`rounded-lg border px-3 py-1.5 text-xs disabled:cursor-not-allowed disabled:opacity-35 ${b ? "border-fuchsia-400 bg-fuchsia-400/15" : "border-zinc-700"}`}>{b ? "Selected B" : "Track B"}</button></div></div>; })}</div>}
    {!loading && tracks.length === 0 && query && !error && <p className="py-4 text-center text-sm text-text-secondary">Search for a song, artist or DJ set to begin.</p>}
    {error && <p role="alert" className="rounded-xl border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-200">{error}</p>}
  </div>;
}
