"use client";

import { SpotifyProGate } from "@/components/spotify/SpotifyProGate";
import type { SpotifySelectedTrack } from "@/types/spotify";

interface SpotifyAnalyzerSourceProps {
  selectedTrackA: SpotifySelectedTrack | null;
  selectedTrackB: SpotifySelectedTrack | null;
  onSelectTrack: (track: SpotifySelectedTrack) => void;
  onDeselectTrack: (position: "track_a" | "track_b") => void;
  onBack: () => void;
}

export function SpotifyAnalyzerSource({}: SpotifyAnalyzerSourceProps) {
  return <SpotifyProGate />;
}
