"use client";

import { useState } from "react";
import { CirclePlay, Loader2, Search } from "lucide-react";

import { youtubeService } from "@/services/youtube-service";
import type { YouTubeTrack } from "@/types/youtube-track";

interface Props { selectedTrackA: YouTubeTrack | null; selectedTrackB: YouTubeTrack | null; onSelect: (track: YouTubeTrack, position: "track_a" | "track_b") => void; onDeselect: (position: "track_a" | "track_b") => void }

export function YouTubeAnalyzerSource({ selectedTrackA, selectedTrackB, onSelect, onDeselect }: Props) {
  const [query, setQuery] = useState("");
  const [tracks, setTracks] = useState<YouTubeTrack[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function search() { if (!query.trim()) return; setLoading(true); setError(null); try { setTracks((await youtubeService.search(query.trim())).items); } catch (cause) { setError(cause instanceof Error ? cause.message : "YouTube search failed."); } finally { setLoading(false); } }
  return <div className="space-y-5">
    <div className="flex gap-2"><div className="relative min-w-0 flex-1"><Search className="absolute left-4 top-3.5 h-4 w-4 text-text-secondary" /><input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void search(); }} placeholder="Search music on YouTube" className="w-full rounded-xl border border-zinc-700 bg-zinc-900 py-3 pl-11 pr-4 text-sm text-text outline-none focus:border-red-500" /></div><button type="button" onClick={() => void search()} className="rounded-xl bg-red-600 px-5 text-sm font-bold text-white">Search</button></div>
    {loading && <div className="flex justify-center p-6"><Loader2 className="h-5 w-5 animate-spin text-red-500" /></div>}
    {!loading && tracks.length > 0 && <div className="max-h-[34rem] space-y-2 overflow-y-auto">{tracks.map((track) => { const a = selectedTrackA?.id === track.id; const b = selectedTrackB?.id === track.id; return <div key={track.id} className="flex items-center gap-3 rounded-xl border border-zinc-800 bg-zinc-900/50 p-3"><div className="flex h-12 w-20 shrink-0 items-center justify-center rounded bg-zinc-800 bg-cover bg-center" style={track.thumbnail ? { backgroundImage: `url(${track.thumbnail})` } : undefined}>{!track.thumbnail && <CirclePlay className="h-8 w-8 text-red-500" />}</div><div className="min-w-0 flex-1"><strong className="block truncate text-sm text-text">{track.title}</strong><span className="block truncate text-xs text-text-secondary">{track.channel}</span></div><button type="button" disabled={b} onClick={() => a ? onDeselect("track_a") : onSelect(track, "track_a")} className={`rounded-lg border px-3 py-1.5 text-xs ${a ? "border-cyan-400 bg-cyan-400/15" : "border-zinc-700"}`}>Track A</button><button type="button" disabled={a} onClick={() => b ? onDeselect("track_b") : onSelect(track, "track_b")} className={`rounded-lg border px-3 py-1.5 text-xs ${b ? "border-fuchsia-400 bg-fuchsia-400/15" : "border-zinc-700"}`}>Track B</button></div>; })}</div>}
    {error && <p className="rounded-xl border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-200">{error}</p>}
  </div>;
}
