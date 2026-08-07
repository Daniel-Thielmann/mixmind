import { cn } from "@/lib/utils";

function Progress({ value = 0, className, indicatorClassName, ...props }: React.HTMLAttributes<HTMLDivElement> & { value?: number; indicatorClassName?: string }) {
  const normalized = Math.min(100, Math.max(0, value));
  return <div role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={normalized} className={cn("relative h-2 w-full overflow-hidden rounded-full bg-secondary", className)} {...props}><div className={cn("h-full w-full flex-1 bg-primary transition-transform", indicatorClassName)} style={{ transform: `translateX(-${100 - normalized}%)` }} /></div>;
}
export { Progress };
