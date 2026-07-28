"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  ChevronDown,
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

const SEARCH_LIMIT = 10;

function extractTrackFromItem(
  item: Record<string, unknown>,
  position: "track_a" | "track_b",
): SpotifySelectedTrack | null {
  const track =
    (item.item as Record<string, unknown>) ??
    (item.track as Record<string, unknown>) ??
    item;
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
  const [searchOffset, setSearchOffset] = useState(0);
  const [searchTotal, setSearchTotal] = useState(0);
  const [searchHasMore, setSearchHasMore] = useState(false);
  const [searchLoadingMore, setSearchLoadingMore] = useState(false);
  const [selectedPlaylistId, setSelectedPlaylistId] = useState<string | null>(null);
  const [playlistTotal, setTotal] = useState(0);
  const [playlistOffset, setPlaylistOffset] = useState(0);
  const [spotifyUserId, setSpotifyUserId] = useState<string | null>(null);
  const initialLoadDone = useRef(false);
  const loadingRef = useRef(false);
  const searchAbortRef = useRef<AbortController | null>(null);
  const lastSearchRef = useRef<string>("");
  const searchCounterRef = useRef(0);

  const limit = 20;

  function extractPlaylists(paging: SpotifyPaging): SpotifyPlaylistSummary[] {
    return (paging.items ?? []) as unknown as SpotifyPlaylistSummary[];
  }

  const loadData = useCallback(async () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    setError(null);

    try {
      if (source === "playlists" && !selectedPlaylistId) {
        const data = await fetchSpotifyData<SpotifyPaging>("playlists", {
          limit: String(limit),
          offset: String(playlistOffset),
        });
        const allPlaylists = extractPlaylists(data);
        if (spotifyUserId) {
          setPlaylists(
            allPlaylists.filter(
              (p) => p.owner.id === spotifyUserId || p.collaborative === true,
            ),
          );
        } else {
          setPlaylists(allPlaylists);
        }
        setTotal(data.total);
      } else if (selectedPlaylistId) {
        const data = await fetchSpotifyData<SpotifyPaging>("playlist-tracks", {
          playlist_id: selectedPlaylistId,
          limit: String(limit),
          offset: String(playlistOffset),
        });
        const extracted = data.items
          .map((item) => extractTrackFromItem(item, "track_a"))
          .filter((t): t is SpotifySelectedTrack => t !== null);
        setTracks(extracted);
        setTotal(data.total);
      } else if (source === "saved") {
        const data = await fetchSpotifyData<SpotifyPaging>("saved-tracks", {
          limit: String(limit),
          offset: String(playlistOffset),
        });
        const extracted = data.items
          .map((item) => extractTrackFromItem(item, "track_a"))
          .filter((t): t is SpotifySelectedTrack => t !== null);
        setTracks(extracted);
        setTotal(data.total);
      }
    } catch (cause) {
      const msg = cause instanceof Error ? cause.message : "Failed to load Spotify data";
      if (msg.includes("cannot be accessed") || msg.includes("403")) {
        setError(
          "Spotify API only allows browsing tracks for playlists you own. " +
            "Search for specific tracks instead, or select an owned playlist.",
        );
      } else {
        setError(msg);
      }
    } finally {
      loadingRef.current = false;
      setLoading(false);
    }
  }, [source, selectedPlaylistId, playlistOffset, spotifyUserId]);

  useEffect(() => {
    if (source !== "search") {
      void loadData();
    }
  }, [loadData, source]);

  useEffect(() => {
    async function fetchUserId() {
      try {
        const statusRes = await fetch("/api/integrations/spotify?action=status", { cache: "no-store" });
        if (statusRes.ok) {
          const statusData = (await statusRes.json()) as { spotify_user_id?: string };
          if (statusData.spotify_user_id) {
            setSpotifyUserId(statusData.spotify_user_id);
          }
        }
      } catch {
        // non-critical
      }
    }
    if (!initialLoadDone.current) {
      initialLoadDone.current = true;
      void fetchUserId();
    }
  }, []);

  useEffect(() => {
    if (source === "search") {
      setLoading(false);
    }
  }, [source]);

  function handleSelectPlaylist(playlist: SpotifyPlaylistSummary) {
    setSelectedPlaylistId(playlist.id);
    setPlaylistOffset(0);
  }

  function handleBackToPlaylists() {
    setSelectedPlaylistId(null);
    setTracks([]);
    setPlaylistOffset(0);
  }

  function handleSourceChange(newSource: SpotifySourceType) {
    if (searchAbortRef.current) {
      searchAbortRef.current.abort();
      searchAbortRef.current = null;
    }
    setSource(newSource);
    setSelectedPlaylistId(null);
    setTracks([]);
    setPlaylistOffset(0);
    setError(null);
    setSearchTotal(0);
    setSearchHasMore(false);
    setSearchOffset(0);
    setSearchLoadingMore(false);
    if (newSource !== "search") {
      setSearchQuery("");
    }
  }

  async function performSearch(query: string, append: boolean) {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setError("Enter at least 2 characters to search.");
      return;
    }

    if (searchAbortRef.current) {
      searchAbortRef.current.abort();
    }
    const controller = new AbortController();
    searchAbortRef.current = controller;
    const counter = ++searchCounterRef.current;
    lastSearchRef.current = trimmed;

    if (!append) {
      setTracks([]);
      setSearchOffset(0);
      setSearchTotal(0);
      setSearchHasMore(false);
      setError(null);
      setLoading(true);
    } else {
      setSearchLoadingMore(true);
    }

    try {
      const targetOffset = append ? searchOffset + SEARCH_LIMIT : 0;
      const params: Record<string, string> = { q: trimmed, offset: String(targetOffset) };
      const data = await fetchSpotifyData<SpotifyPaging>("search", params);

      if (controller.signal.aborted) return;
      if (counter !== searchCounterRef.current) return;

      const extracted = data.items
        .map((item) => extractTrackFromItem(item, "track_a"))
        .filter((t): t is SpotifySelectedTrack => t !== null);

      if (append) {
        setTracks((prev) => [...prev, ...extracted]);
      } else {
        setTracks(extracted);
      }
      setSearchTotal(data.total);
      setSearchOffset(targetOffset);
      setSearchHasMore(targetOffset + SEARCH_LIMIT < data.total);
      setError(null);
    } catch (cause) {
      if (cause instanceof DOMException && cause.name === "AbortError") return;
      const msg = cause instanceof Error ? cause.message : "We couldn\u2019t complete this Spotify search. Please try again.";
      if (!msg.includes("AbortError")) {
        setError(msg);
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
        setSearchLoadingMore(false);
      }
    }
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    void performSearch(searchQuery, false);
  }

  function handleLoadMore() {
    void performSearch(searchQuery, true);
  }

  function handleSearchKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      void performSearch(searchQuery, false);
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
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            placeholder="Search by track, artist, or album..."
            minLength={2}
            className="flex-1 rounded-xl border border-zinc-700 bg-zinc-900/70 px-4 py-2.5 text-sm text-text outline-none transition-colors placeholder:text-text-secondary/50 focus:border-primary/50"
          />
          <button
            type="submit"
            disabled={searchQuery.trim().length < 2 || loading}
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

      {source === "search" && searchTotal > 0 && tracks.length > 0 && (
        <p className="text-xs text-text-secondary">
          {searchTotal} result{searchTotal !== 1 ? "s" : ""}
          {" \u2022 "}showing {tracks.length}
        </p>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-danger/30 bg-danger/5 px-4 py-8 text-center">
          <AlertCircle className="h-8 w-8 text-danger" />
          <p className="text-sm text-red-200">{error}</p>
          {source === "search" ? (
            <button
              onClick={() => void performSearch(searchQuery, false)}
              className="flex items-center gap-1.5 rounded-lg bg-danger/15 px-3 py-1.5 text-xs font-medium text-danger transition-colors hover:bg-danger/25"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Retry
            </button>
          ) : (
            <button
              onClick={() => void loadData()}
              className="flex items-center gap-1.5 rounded-lg bg-danger/15 px-3 py-1.5 text-xs font-medium text-danger transition-colors hover:bg-danger/25"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Retry
            </button>
          )}
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
                  {(() => {
                    const count =
                      playlist.items?.total ??
                      playlist.tracks?.total;
                    if (count == null) return "Track count unavailable";
                    return `${count} ${count === 1 ? "track" : "tracks"}`;
                  })()}
                </p>
              </div>
            </button>
          ))}
          {playlists.length === 0 && (
            <p className="col-span-2 py-8 text-center text-sm text-text-secondary">
              {spotifyUserId
                ? "No owned or collaborative playlists found. Only playlists you created or collaborate on can be used."
                : "No playlists found."}
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {tracks.length === 0 && !loading ? (
            <p className="py-8 text-center text-sm text-text-secondary">
              {source === "search"
                ? "Enter at least 2 characters and press Search to find tracks."
                : "No tracks found."}
            </p>
          ) : (
            <>
              {tracks.map((track) => (
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
              ))}
              {source === "search" && searchHasMore && (
                <div className="flex justify-center pt-2">
                  <button
                    onClick={handleLoadMore}
                    disabled={searchLoadingMore}
                    className="flex items-center gap-1.5 rounded-lg bg-zinc-800/50 px-4 py-2 text-xs font-medium text-text-secondary transition-colors hover:bg-zinc-800 disabled:opacity-50"
                  >
                    {searchLoadingMore ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                    Load more
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
