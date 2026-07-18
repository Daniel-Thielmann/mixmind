export type VideoPlayerStatus =
  | "idle"
  | "loading"
  | "ready"
  | "playing"
  | "paused"
  | "ended"
  | "error";

export interface VideoPlayerProps {
  videoId: string;
  startTime: number;
  endTime: number;
  autoplay?: boolean;
  muted?: boolean;
  loop?: boolean;
  controls?: boolean;
  poster?: string;
  className?: string;
  onPlayStateChange?: (playing: boolean) => void;
  onTimeUpdate?: (relativeTime: number) => void;
}
