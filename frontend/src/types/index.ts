export interface AudioAnalysis {
  filename: string;
  duration: number;
  sample_rate: number;
  bpm: number;
  energy: number;
  key?: string;       // KEY added
  camelot?: string;  // Camelot Whell added
}

export interface CompatibilityResult {
  compatibility_score: number;
  tempo_difference: number;
  energy_difference: number;
  tempo_match: string;
  energy_match: string;
  harmonic_match?: string;  // Nova métrica: compatibilidade harmônica
  overall_rating: string;
}

export interface ImageAsset {
  image_path: string;
}

export interface TrackMediaAssets {
  track_a: ImageAsset;
  track_b: ImageAsset;
}

export interface TempoAnalysis {
  difference: string;
  recommendation: string;
}

export interface EnergyAnalysis {
  difference: string;
  recommendation: string;
}

export interface CompatibilityAnalysis {
  score: string;
  interpretation: string;
}

export interface MixStrategy {
  before_transition: string;
  during_transition: string;
  after_transition: string;
}

export interface DJExecution {
  loop: string;
  eq: string;
  filter: string;
  tempo_fader: string;
  phrase_matching: string;
  cue_point: string;
}

export interface AIRecommendationResponse {
  ai_provider?: string;
  ai_model?: string;
  ai_latency?: number;
  ai_retry_count?: number;
  ai_fallback_occurred?: boolean;
  summary: string;
  mix_direction: string;
  transition_quality: string;
  transition_type: string;
  confidence: number;
  tempo_analysis: TempoAnalysis;
  energy_analysis: EnergyAnalysis;
  compatibility_analysis: CompatibilityAnalysis;
  mix_strategy: MixStrategy;
  dj_execution: DJExecution;
  club_tip: string;
  professional_notes: string;
  risks: string[];
  best_use_case: string;
  risk_level: string;
  mix_difficulty: string;
  recommended_transition_length: string;
  alternative_strategy: string;
  dj_score: number;
  why_this_strategy: string;
  transition_timeline: Record<string, string>;
}

export interface UploadAnalysisResponse {
  status: string;
  message: string;
  analysis_id: string;
  track_a: AudioAnalysis;
  track_b: AudioAnalysis;
  compatibility: CompatibilityResult;
  ai_recommendation: AIRecommendationResponse;
  waveforms: TrackMediaAssets;
  spectrograms: TrackMediaAssets;
}

export type UploadStatus =
  | "idle"
  | "uploading"
  | "processing"
  | "success"
  | "error";
