"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  ListMusic,
  Loader2,
  Music,
  RefreshCw,
  Search,
  Heart,
} from "lucide-react";

import { TrackCard } from "@/components/spotify/TrackCard";
import { fetchSpotifyData } from "@/services/spotify-service";
import type {
  SpotifyPaging,
  SpotifyPlaylistSummary,
  SpotifySelectedTrack,
  SpotifySourceType,
} from "@/types/spotify";

interface SpotifySelectorProps {
  selectedTrackA: SpotifySelectedTrack | null;
  selectedTrackB: SpotifySelectedTrack | null;
  onSelectTrack: (track: SpotifySelectedTrack) => void;
  onDeselectTrack: (position: "track_a" | "track_b") => void;
  onBack: () => void;
}

function extractTrackFromItem(
  item: Record<string, unknown>,
  position: "track_a" | "track_b",
): SpotifySelectedTrack | null {
  const track = (item.track as Record<string, unknown>) ?? item;
  if (!track?.id || typeof track.id !== "string") return null;

  const artists = (track.artists as Array<{ name: string }>) ?? [];
  const album = (track.album as Record<string, unknown>) ?? {};
  const images = (album.images as Array<{ url: string }>) ?? [];

  return {
    id: track.id as string,
    name: (track.name as string) ?? "Unknown",
    artists: artists.map((a) => a.name).join(", "),
    album: (album.name as string) ?? "Unknown",
    albumArt: images[0]?.url,
    durationMs: (track.duration_ms as number) ?? 0,
    position,
  };
}

export function SpotifySelector({
  selectedTrackA,
  selectedTrackB,
  onSelectTrack,
  onDeselectTrack,
  onBack,
}: SpotifySelectorProps) {
  const [source, setSource] = useState<SpotifySourceType>("playlists");
  const [playlists, setPlaylists] = useState<SpotifyPlaylistSummary[]>([]);
  const [tracks, setTracks] = useState<SpotifySelectedTrack[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPlaylistId, setSelectedPlaylistId] = useState<string | null>(null);
  const [, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);

  const limit = 20;

  function extractPlaylists(paging: SpotifyPaging): SpotifyPlaylistSummary[] {
    return (paging.items ?? []) as unknown as SpotifyPlaylistSummary[];
  }

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (source === "playlists" && !selectedPlaylistId) {
        const data = await fetchSpotifyData<SpotifyPaging>("playlists", {
          limit: String(limit),
          offset: String(offset),
        });
        setPlaylists(extractPlaylists(data));
        setTotal(data.total);
      } else if (selectedPlaylistId) {
        const data = await fetchSpotifyData<SpotifyPaging>("playlist-tracks", {
          playlist_id: selectedPlaylistId,
          limit: String(limit),
          offset: String(offset),
        });
        const extracted = data.items
          .map((item) => extractTrackFromItem(item, "track_a"))
          .filter((t): t is SpotifySelectedTrack => t !== null);
        setTracks(extracted);
        setTotal(data.total);
      } else if (source === "saved") {
        const data = await fetchSpotifyData<SpotifyPaging>("saved-tracks", {
          limit: String(limit),
          offset: String(offset),
        });
        const extracted = data.items
          .map((item) => extractTrackFromItem(item, "track_a"))
          .filter((t): t is SpotifySelectedTrack => t !== null);
        setTracks(extracted);
        setTotal(data.total);
      } else if (source === "search" && searchQuery.trim()) {
        const data = await fetchSpotifyData<SpotifyPaging>("search", {
          q: searchQuery.trim(),
          limit: String(limit),
          offset: String(offset),
        });
        const extracted = data.items
          .map((item) => extractTrackFromItem(item, "track_a"))
          .filter((t): t is SpotifySelectedTrack => t !== null);
        setTracks(extracted);
        setTotal(data.total);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to load Spotify data");
    } finally {
      setLoading(false);
    }
  }, [source, selectedPlaylistId, offset, searchQuery]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadData();
  }, [loadData]);

  function handleSelectPlaylist(playlist: SpotifyPlaylistSummary) {
    setSelectedPlaylistId(playlist.id);
    setOffset(0);
  }

  function handleBackToPlaylists() {
    setSelectedPlaylistId(null);
    setTracks([]);
    setOffset(0);
  }

  function handleSourceChange(newSource: SpotifySourceType) {
    setSource(newSource);
    setSelectedPlaylistId(null);
    setTracks([]);
    setOffset(0);
    setError(null);
    if (newSource !== "search") {
      setSearchQuery("");
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setOffset(0);
    if (searchQuery.trim()) {
      void loadData();
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-[0.15em] text-text-secondary">
          Select from Spotify
        </h3>
        <button
          onClick={onBack}
          className="text-xs text-text-secondary underline underline-offset-2 transition-colors hover:text-text"
        >
          Back to upload
        </button>
      </div>

      {selectedTrackA || selectedTrackB ? (
        <div className="flex flex-wrap gap-3">
          {selectedTrackA && (
            <TrackCard
              track={selectedTrackA}
              selectedAs="track_a"
              onSelect={() => {}}
              onDeselect={() => onDeselectTrack("track_a")}
            />
          )}
          {selectedTrackB && (
            <TrackCard
              track={selectedTrackB}
              selectedAs="track_b"
              onSelect={() => {}}
              onDeselect={() => onDeselectTrack("track_b")}
            />
          )}
        </div>
      ) : null}

      <div className="flex gap-2">
        {(["playlists", "saved", "search"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => handleSourceChange(tab)}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all ${
              source === tab
                ? "bg-primary/15 text-primary"
                : "bg-zinc-800/50 text-text-secondary hover:bg-zinc-800"
            }`}
          >
            {tab === "playlists" && <ListMusic className="h-3.5 w-3.5" />}
            {tab === "saved" && <Heart className="h-3.5 w-3.5" />}
            {tab === "search" && <Search className="h-3.5 w-3.5" />}
            {tab === "playlists" && "Playlists"}
            {tab === "saved" && "Saved Tracks"}
            {tab === "search" && "Search"}
          </button>
        ))}
      </div>

      {source === "search" ? (
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by track, artist, or album..."
            className="flex-1 rounded-xl border border-zinc-700 bg-zinc-900/70 px-4 py-2.5 text-sm text-text outline-none transition-colors placeholder:text-text-secondary/50 focus:border-primary/50"
          />
          <button
            type="submit"
            disabled={!searchQuery.trim() || loading}
            className="flex items-center gap-1.5 rounded-xl bg-primary/15 px-4 py-2.5 text-sm font-medium text-primary transition-colors hover:bg-primary/25 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            Search
          </button>
        </form>
      ) : null}

      {selectedPlaylistId ? (
        <button
          onClick={handleBackToPlaylists}
          className="text-xs text-text-secondary underline underline-offset-2 transition-colors hover:text-text"
        >
          &larr; Back to playlists
        </button>
      ) : null}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-danger/30 bg-danger/5 px-4 py-8 text-center">
          <AlertCircle className="h-8 w-8 text-danger" />
          <p className="text-sm text-red-200">{error}</p>
          <button
            onClick={() => void loadData()}
            className="flex items-center gap-1.5 rounded-lg bg-danger/15 px-3 py-1.5 text-xs font-medium text-danger transition-colors hover:bg-danger/25"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Retry
          </button>
        </div>
      ) : source === "playlists" && !selectedPlaylistId ? (
        <div className="grid gap-2 sm:grid-cols-2">
          {playlists.map((playlist) => (
            <button
              key={playlist.id}
              onClick={() => handleSelectPlaylist(playlist)}
              className="flex items-center gap-3 rounded-xl border border-zinc-800 bg-card/50 p-3 text-left transition-all hover:border-zinc-700"
            >
              {playlist.images?.[0]?.url ? (
                <img
                  src={playlist.images[0].url}
                  alt={playlist.name}
                  className="h-12 w-12 flex-shrink-0 rounded-lg object-cover"
                />
              ) : (
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-zinc-800">
                  <Music className="h-5 w-5 text-text-secondary" />
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-text">
                  {playlist.name}
                </p>
                <p className="text-xs text-text-secondary">
                  {playlist.tracks?.total ?? 0} tracks
                </p>
              </div>
            </button>
          ))}
          {playlists.length === 0 && (
            <p className="col-span-2 py-8 text-center text-sm text-text-secondary">
              No playlists found.
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {tracks.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-secondary">
              {source === "search"
                ? "Search for tracks above."
                : "No tracks found."}
            </p>
          ) : (
            tracks.map((track) => (
              <TrackCard
                key={track.id}
                track={track}
                selectedAs={
                  selectedTrackA?.id === track.id
                    ? "track_a"
                    : selectedTrackB?.id === track.id
                      ? "track_b"
                      : undefined
                }
                onSelect={(position) =>
                  onSelectTrack({ ...track, position })
                }
                onDeselect={() => {
                  if (selectedTrackA?.id === track.id) {
                    onDeselectTrack("track_a");
                  } else if (selectedTrackB?.id === track.id) {
                    onDeselectTrack("track_b");
                  }
                }}
                disabled={
                  (selectedTrackA !== null && selectedTrackB !== null) ||
                  (selectedTrackA?.id === track.id) ||
                  (selectedTrackB?.id === track.id)
                }
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}
