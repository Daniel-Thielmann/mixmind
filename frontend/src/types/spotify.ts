export interface SpotifyTrackSummary {
  id: string;
  name: string;
  artists: { id: string; name: string }[];
  album: {
    id: string;
    name: string;
    images: { url: string; width: number; height: number }[];
  };
  duration_ms: number;
  external_urls: { spotify: string };
  popularity: number;
}

export interface SpotifyPaging {
  href: string;
  items: Record<string, unknown>[];
  limit: number;
  next: string | null;
  offset: number;
  previous: string | null;
  total: number;
}

export interface SpotifyPlaylistSummary {
  id: string;
  name: string;
  description: string;
  images: { url: string }[];
  tracks?: { total: number };
  items?: { total: number; items?: Record<string, unknown>[] };
  owner: { display_name: string; id: string };
  snapshot_id: string;
  collaborative: boolean;
}

export interface SpotifySelectedTrack {
  id: string;
  name: string;
  artists: string;
  album: string;
  albumArt: string;
  durationMs: number;
  position: "track_a" | "track_b";
}

export interface SpotifyAnalysisRequest {
  tracks: {
    position: "track_a" | "track_b";
    spotify_track_id: string;
  }[];
}

export type SpotifySourceType = "playlists" | "saved" | "search";
