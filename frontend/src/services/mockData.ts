import type { UploadAnalysisResponse } from "@/types";

export const mockAnalysis: UploadAnalysisResponse = {
  status: "success",
  message: "Analysis completed successfully",
  track_a: {
    filename: "track_a.mp3",
    duration: 234.5,
    sample_rate: 44100,
    bpm: 128,
    energy: 0.75,
  },
  track_b: {
    filename: "track_b.mp3",
    duration: 198.2,
    sample_rate: 44100,
    bpm: 124,
    energy: 0.62,
  },
  compatibility: {
    compatibility_score: 85,
    tempo_difference: 4,
    energy_difference: 0.13,
    tempo_match: "close",
    energy_match: "moderate",
    overall_rating: "good",
  },
};
