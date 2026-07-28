import type { UploadAnalysisResponse } from "@/types";
import type { SpotifyAnalysisRequest } from "@/types/spotify";

const FRIENDLY_ERROR_MESSAGE = "Unable to analyze the selected tracks. Please try again.";

export async function fetchSpotifyData<T>(
  action: string,
  params?: Record<string, string>,
): Promise<T> {
  const searchParams = new URLSearchParams({ action, ...(params ?? {}) }).toString();
  const response = await fetch(`/api/spotify?${searchParams}`, {
    cache: "no-store",
    signal: AbortSignal.timeout(40000),
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string; error_type?: string } | null;
    const detail = payload?.detail ?? `Failed to fetch Spotify data: ${action}`;
    const error = new Error(detail);
    if (payload?.error_type) {
      (error as Error & { error_type?: string }).error_type = payload.error_type;
    }
    throw error;
  }
  return response.json() as Promise<T>;
}

export async function analyzeSpotifyTracks(
  request: SpotifyAnalysisRequest,
): Promise<UploadAnalysisResponse> {
  try {
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
