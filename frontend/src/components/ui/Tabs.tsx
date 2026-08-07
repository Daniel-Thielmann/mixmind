"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type TabsContextValue = { value: string; setValue: (value: string) => void; baseId: string };
const TabsContext = React.createContext<TabsContextValue | null>(null);

function useTabs() {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error("Tabs components must be used within Tabs");
  return context;
}

function Tabs({ defaultValue = "", value, onValueChange, className, ...props }: React.HTMLAttributes<HTMLDivElement> & { defaultValue?: string; value?: string; onValueChange?: (value: string) => void }) {
  const [internalValue, setInternalValue] = React.useState(defaultValue);
  const baseId = React.useId();
  const currentValue = value ?? internalValue;
  const setValue = React.useCallback((next: string) => { if (value === undefined) setInternalValue(next); onValueChange?.(next); }, [onValueChange, value]);
  return <TabsContext.Provider value={{ value: currentValue, setValue, baseId }}><div className={cn(className)} {...props} /></TabsContext.Provider>;
}

const TabsList = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, onKeyDown, ...props }, ref) => (
  <div ref={ref} role="tablist" className={cn("inline-flex h-10 items-center justify-center rounded-lg border border-border/60 bg-muted p-1 text-muted-foreground", className)} onKeyDown={(event) => { onKeyDown?.(event); if (event.defaultPrevented || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return; const tabs = Array.from(event.currentTarget.querySelectorAll<HTMLElement>('[role="tab"]:not([disabled])')); const current = tabs.indexOf(document.activeElement as HTMLElement); const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length; tabs[next]?.focus(); tabs[next]?.click(); event.preventDefault(); }} {...props} />
));
TabsList.displayName = "TabsList";

const TabsTrigger = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & { value: string }>(({ className, value, ...props }, ref) => {
  const tabs = useTabs(); const selected = tabs.value === value;
  const { onClick, ...triggerProps } = props;
  return <button ref={ref} type="button" role="tab" id={`${tabs.baseId}-trigger-${value}`} aria-selected={selected} aria-controls={`${tabs.baseId}-content-${value}`} tabIndex={selected ? 0 : -1} className={cn("inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 disabled:pointer-events-none disabled:opacity-50", selected ? "bg-secondary text-foreground shadow-sm" : "hover:text-foreground", className)} onClick={(event) => { onClick?.(event); if (!event.defaultPrevented) tabs.setValue(value); }} {...triggerProps} />;
});
TabsTrigger.displayName = "TabsTrigger";

const TabsContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & { value: string }>(({ className, value, ...props }, ref) => {
  const tabs = useTabs(); if (tabs.value !== value) return null;
  return <div ref={ref} role="tabpanel" id={`${tabs.baseId}-content-${value}`} aria-labelledby={`${tabs.baseId}-trigger-${value}`} tabIndex={0} className={cn("mt-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40", className)} {...props} />;
});
TabsContent.displayName = "TabsContent";

export { Tabs, TabsList, TabsTrigger, TabsContent };
