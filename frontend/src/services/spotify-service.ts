import type { UploadAnalysisResponse } from "@/types";
import type { SpotifyAnalysisRequest } from "@/types/spotify";

const FRIENDLY_ERROR_MESSAGE = "Unable to analyze the selected tracks. Please try again.";
const BACKEND_URL = "http://127.0.0.1:8000";

function getAdminHeaders(): Record<string, string> | null {
  try {
    const raw = sessionStorage.getItem("mixmind_admin_session");
    if (!raw) return null;
    const session = JSON.parse(raw) as { auth: { userId: string; timestamp: string; signature: string } };
    return {
      "X-MixMind-User": session.auth.userId,
      "X-MixMind-Timestamp": session.auth.timestamp,
      "X-MixMind-Signature": session.auth.signature,
    };
  } catch { return null; }
}

function buildSpotifyUrl(action: string, params?: Record<string, string>): string {
  const p = params ?? {};
  const base = `${BACKEND_URL}/api/v1/integrations/spotify`;
  switch (action) {
    case "playlists":
      return `${base}/playlists?limit=${p.limit ?? "20"}&offset=${p.offset ?? "0"}`;
    case "playlist-tracks":
      return `${base}/playlists/${p.playlist_id}/tracks?limit=${p.limit ?? "50"}&offset=${p.offset ?? "0"}`;
    case "saved-tracks":
      return `${base}/saved-tracks?limit=${p.limit ?? "20"}&offset=${p.offset ?? "0"}`;
    case "search":
      return `${base}/search?q=${encodeURIComponent(p.q ?? "")}&limit=${p.limit ?? "10"}&offset=${p.offset ?? "0"}`;
    default:
      throw new Error(`Unknown Spotify action: ${action}`);
  }
}

export async function fetchSpotifyData<T>(
  action: string,
  params?: Record<string, string>,
): Promise<T> {
  const adminHeaders = getAdminHeaders();
  if (adminHeaders) {
    const url = buildSpotifyUrl(action, params);
    const response = await fetch(url, {
      cache: "no-store",
      headers: { ...adminHeaders, "Content-Type": "application/json" },
    });
    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      throw new Error(payload?.detail ?? `Failed to fetch Spotify data: ${action}`);
    }
    return response.json() as Promise<T>;
  }

  const searchParams = new URLSearchParams({ action, ...(params ?? {}) }).toString();
  const response = await fetch(`/api/spotify?${searchParams}`, { cache: "no-store" });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Failed to fetch Spotify data: ${action}`);
  }
  return response.json() as Promise<T>;
}

export async function analyzeSpotifyTracks(
  request: SpotifyAnalysisRequest,
): Promise<UploadAnalysisResponse> {
  try {
    const adminHeaders = getAdminHeaders();
    if (adminHeaders) {
      const response = await fetch(`${BACKEND_URL}/api/v1/analyze/spotify`, {
        method: "POST",
        headers: { ...adminHeaders, "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        if (response.status === 401) throw new Error("You need to sign in before running an analysis.");
        const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(payload?.detail ?? FRIENDLY_ERROR_MESSAGE);
      }
      return (await response.json()) as UploadAnalysisResponse;
    }

    const response = await fetch("/api/analyze/spotify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("You need to sign in before running an analysis.");
      }
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      throw new Error(payload?.detail ?? FRIENDLY_ERROR_MESSAGE);
    }
    return (await response.json()) as UploadAnalysisResponse;
  } catch (error) {
    throw error instanceof Error ? error : new Error(FRIENDLY_ERROR_MESSAGE);
  }
}
