"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getApiUrl } from "@/services/api-config";
import type { DemoMediaManifest } from "@/types/demo-media";

export function useDemoMedia() {
  const targetRef = useRef<HTMLDivElement>(null);
  const [manifest, setManifest] = useState<DemoMediaManifest | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${getApiUrl()}/api/v1/demo/manifest`, {
        credentials: "include",
        cache: "no-store",
      });
      if (!response.ok) throw new Error("Demo media unavailable");
      setManifest(await response.json());
    } catch {
      setError("The real-media demonstration is temporarily unavailable.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const target = targetRef.current;
    if (!target) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        void load();
        observer.disconnect();
      }
    }, { rootMargin: "400px" });
    observer.observe(target);
    return () => observer.disconnect();
  }, [load]);

  useEffect(() => {
    if (!manifest) return;
    const refreshIn = Math.max(30_000, manifest.expiresAt * 1000 - Date.now() - 60_000);
    const timer = window.setTimeout(() => void load(), refreshIn);
    return () => window.clearTimeout(timer);
  }, [manifest, load]);

  return { targetRef, manifest, loading, error, retry: load };
}
