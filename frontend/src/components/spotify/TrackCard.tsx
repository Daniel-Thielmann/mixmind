"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Music, X } from "lucide-react";

interface TrackCardProps {
  track: {
    id: string;
    name: string;
    artists: string;
    album: string;
    albumArt?: string;
    durationMs: number;
  };
  selectedAs?: "track_a" | "track_b";
  onSelect: (position: "track_a" | "track_b") => void;
  onDeselect: () => void;
  disabled?: boolean;
}

function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export function TrackCard({
  track,
  selectedAs,
  onSelect,
  onDeselect,
  disabled,
}: TrackCardProps) {
  return (
    <div
      className={`group flex items-center gap-3 rounded-xl border p-3 transition-all ${
        selectedAs
          ? "border-primary/50 bg-primary/5"
          : "border-zinc-800 bg-card/50 hover:border-zinc-700"
      }`}
    >
      {track.albumArt ? (
        <img
          src={track.albumArt}
          alt={track.album}
          className="h-12 w-12 flex-shrink-0 rounded-lg object-cover"
        />
      ) : (
        <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-zinc-800">
          <Music className="h-5 w-5 text-text-secondary" />
        </div>
      )}

      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-text">
          {track.name}
        </p>
        <p className="truncate text-xs text-text-secondary">
          {track.artists} &middot; {track.album}
        </p>
        <p className="text-xs text-text-secondary">
          {formatDuration(track.durationMs)}
        </p>
      </div>

      <div className="flex flex-shrink-0 items-center gap-2">
        {selectedAs === "track_a" && (
          <span className="flex items-center gap-1 rounded-full bg-primary/15 px-2.5 py-0.5 text-xs font-semibold text-primary">
            <CheckCircle2 className="h-3 w-3" />A
          </span>
        )}
        {selectedAs === "track_b" && (
          <span className="flex items-center gap-1 rounded-full bg-purple-500/15 px-2.5 py-0.5 text-xs font-semibold text-purple-400">
            <CheckCircle2 className="h-3 w-3" />B
          </span>
        )}

        {selectedAs ? (
          <button
            onClick={onDeselect}
            className="flex h-7 w-7 items-center justify-center rounded-full bg-danger/10 text-danger transition-colors hover:bg-danger/20"
            aria-label={`Remove ${track.name} from selection`}
          >
            <X className="h-3.5 w-3.5" />
          </button>
        ) : disabled ? null : (
          <div className="flex gap-1">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSelect("track_a")}
              className="rounded-lg border border-primary/30 px-2.5 py-1 text-xs font-semibold text-primary transition-colors hover:bg-primary/10"
            >
              Track A
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSelect("track_b")}
              className="rounded-lg border border-purple-500/30 px-2.5 py-1 text-xs font-semibold text-purple-400 transition-colors hover:bg-purple-500/10"
            >
              Track B
            </motion.button>
          </div>
        )}
      </div>
    </div>
  );
}
