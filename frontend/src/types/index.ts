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

export interface UploadAnalysisResponse {
  status: string;
  message: string;
  track_a: AudioAnalysis;
  track_b: AudioAnalysis;
  compatibility: CompatibilityResult;
}
