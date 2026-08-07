import { cn } from "@/lib/utils";

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} {...props} />;
}

function SkeletonCard() {
  return <div className="rounded-xl border border-border/60 bg-card/75 p-6 backdrop-blur md:p-7"><Skeleton className="mb-4 h-3 w-24 rounded-full" /><div className="space-y-3"><Skeleton className="h-4 w-full rounded-full" /><Skeleton className="h-4 w-3/4 rounded-full" /><Skeleton className="h-4 w-1/2 rounded-full" /></div></div>;
}

function SkeletonGrid() {
  return <div className="mt-10 w-full space-y-6"><div className="grid gap-6 xl:grid-cols-2"><SkeletonCard /><SkeletonCard /></div><SkeletonCard /><SkeletonCard /></div>;
}

export { Skeleton, SkeletonCard, SkeletonGrid };
