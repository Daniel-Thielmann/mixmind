import type { SpotifySelectedTrack } from "@/types/spotify";

const STORAGE_KEY = "mixmind_spotify_tracks";

interface StoredTracks {
  trackA: SpotifySelectedTrack;
  trackB: SpotifySelectedTrack;
}

function isValidTrack(track: unknown): track is SpotifySelectedTrack {
  if (!track || typeof track !== "object") return false;
  const t = track as Record<string, unknown>;
  return (
    typeof t.id === "string" &&
    t.id.length > 0 &&
    typeof t.name === "string" &&
    typeof t.artists === "string" &&
    typeof t.album === "string" &&
    typeof t.durationMs === "number" &&
    (t.position === "track_a" || t.position === "track_b")
  );
}

function isValidStoredTracks(data: unknown): data is StoredTracks {
  if (!data || typeof data !== "object") return false;
  const d = data as Record<string, unknown>;
  if (!isValidTrack(d.trackA) || !isValidTrack(d.trackB)) return false;
  return d.trackA.id !== d.trackB.id;
}

export function saveSpotifyTracks(
  trackA: SpotifySelectedTrack,
  trackB: SpotifySelectedTrack,
): boolean {
  try {
    if (trackA.id === trackB.id) return false;
    const data: StoredTracks = {
      trackA: { ...trackA, position: "track_a" },
      trackB: { ...trackB, position: "track_b" },
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    return true;
  } catch {
    return false;
  }
}

export function loadSpotifyTracks(): StoredTracks | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!isValidStoredTracks(parsed)) {
      sessionStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return parsed;
  } catch {
    sessionStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function clearSpotifyTracks(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
  }
}
