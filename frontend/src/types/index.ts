export interface AudioAnalysis {
  filename: string;
  duration: number;
  sample_rate: number;
  bpm: number;
  energy: number;
}

export interface CompatibilityResult {
  compatibility_score: number;
  tempo_difference: number;
  energy_difference: number;
  tempo_match: string;
  energy_match: string;
  overall_rating: string;
}

export interface ImageAsset {
  image_path: string;
}

export interface TrackMediaAssets {
  track_a: ImageAsset;
  track_b: ImageAsset;
}

export interface UploadAnalysisResponse {
  status: string;
  message: string;
  track_a: AudioAnalysis;
  track_b: AudioAnalysis;
  compatibility: CompatibilityResult;
  waveforms: TrackMediaAssets;
  spectrograms: TrackMediaAssets;
}

export type UploadStatus =
  | "idle"
  | "uploading"
  | "processing"
  | "success"
  | "error";
