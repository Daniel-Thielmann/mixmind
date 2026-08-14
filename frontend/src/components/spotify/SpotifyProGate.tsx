import Link from "next/link";
import { LockKeyhole, Music } from "lucide-react";

interface SpotifyProGateProps {
  compact?: boolean;
}

export function SpotifyProGate({ compact = false }: SpotifyProGateProps) {
  return (
    <section className={`rounded-2xl border border-amber-400/25 bg-amber-400/5 ${compact ? "p-5" : "p-6 md:p-8"}`} aria-labelledby="spotify-pro-title">
      <div className="flex items-start gap-4">
        <div className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[#1DB954]/10">
          <Music className="h-6 w-6 text-[#1DB954]" />
          <span className="absolute -bottom-1 -right-1 rounded-full bg-amber-300 p-1 text-black"><LockKeyhole className="h-3 w-3" /></span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 id="spotify-pro-title" className="font-semibold text-text">Spotify integration</h2>
            <span className="rounded-full border border-amber-300/30 bg-amber-300/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-amber-200">Pro</span>
          </div>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Spotify access is reserved for Pro accounts while Spotify limits this integration to approved users. YouTube search and audio upload remain available.
          </p>
          <Link href="/#pricing" className="mt-4 inline-flex rounded-lg border border-amber-300/30 px-3 py-2 text-xs font-semibold text-amber-200 transition-colors hover:bg-amber-300/10">
            View Pro plans
          </Link>
        </div>
      </div>
    </section>
  );
}
