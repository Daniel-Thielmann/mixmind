import type { UploadAnalysisResponse } from "@/types";
import type { YouTubeTrack } from "@/types/youtube-track";

async function json<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? "YouTube request failed.");
  return body as T;
}

export const youtubeService = {
  search: (query: string) => fetch(`/api/youtube?action=search&q=${encodeURIComponent(query)}`, { cache: "no-store" }).then(json<{ items: YouTubeTrack[] }>),
  analyze: (trackA: YouTubeTrack, trackB: YouTubeTrack) => fetch("/api/analyze/youtube", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tracks: [{ position: "track_a", youtube_video_id: trackA.id }, { position: "track_b", youtube_video_id: trackB.id }] }) }).then(json<UploadAnalysisResponse>),
};
