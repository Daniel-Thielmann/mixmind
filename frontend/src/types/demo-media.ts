export interface DemoMediaAsset {
  title: string;
  source: string;
  objectPath: string;
  url: string;
  mimeType: string;
  sizeBytes: number;
  duration?: number;
  originalStart?: number;
  originalEnd?: number;
  checksum: string;
  processedAt: string;
  pipelineVersion: string;
  attribution: string;
}

export interface DemoMediaManifest {
  id: string;
  title: string;
  relationship: string;
  expiresAt: number;
  assets: Record<"trackA" | "trackB" | "transition" | "video" | "poster", DemoMediaAsset>;
}

const REQUIRED_ASSETS = ["trackA", "trackB", "transition", "video", "poster"] as const;

export function isDemoMediaManifest(value: unknown): value is DemoMediaManifest {
  if (!value || typeof value !== "object") return false;
  const manifest = value as Partial<DemoMediaManifest>;
  if (!manifest.assets || typeof manifest.expiresAt !== "number") return false;
  return REQUIRED_ASSETS.every((name) => {
    const asset = manifest.assets?.[name];
    return !!asset && typeof asset.url === "string" && asset.url.startsWith("http") &&
      typeof asset.objectPath === "string" && typeof asset.mimeType === "string" &&
      typeof asset.checksum === "string";
  });
}
