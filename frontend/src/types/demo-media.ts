export interface DemoMediaAsset {
  objectPath: string;
  url: string;
  mimeType: string;
  sizeBytes: number;
  duration?: number;
  checksum: string;
}

export interface DemoMediaManifest {
  id: string;
  title: string;
  source: string;
  processedAt: string;
  pipelineVersion: string;
  attribution: string;
  expiresAt: number;
  assets: Record<"trackA" | "trackB" | "transition" | "video" | "poster", DemoMediaAsset>;
}
