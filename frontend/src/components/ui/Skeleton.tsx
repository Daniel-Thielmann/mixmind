export function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-card/75 p-6 shadow-[0_20px_60px_-35px_rgba(0,0,0,0.9)] backdrop-blur md:p-7">
      <div className="mb-4 h-3 w-24 rounded-full bg-zinc-800/80 animate-pulse" />
      <div className="space-y-3">
        <div className="h-4 w-full rounded-full bg-zinc-800/60 animate-pulse" />
        <div className="h-4 w-3/4 rounded-full bg-zinc-800/60 animate-pulse" />
        <div className="h-4 w-1/2 rounded-full bg-zinc-800/60 animate-pulse" />
      </div>
    </div>
  );
}

export function SkeletonGrid() {
  return (
    <div className="mt-10 w-full space-y-6">
      <div className="grid gap-6 xl:grid-cols-2">
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <SkeletonCard />
      <SkeletonCard />
    </div>
  );
}
