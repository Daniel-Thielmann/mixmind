import type { UploadAnalysisResponse } from "@/types";

import { getApiUrl } from "./api-config";

const ANALYZE_ENDPOINT = "/api/v1/analysis/analyze";
const FRIENDLY_ERROR_MESSAGE =
  "Unable to analyze the selected tracks. Please try again.";

export class ApiService {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = (baseUrl ?? getApiUrl()).replace(/\/$/, "");
  }

  async analyzeTracks(
    trackA: File,
    trackB: File,
  ): Promise<UploadAnalysisResponse> {
    const formData = new FormData();
    formData.append("track_a", trackA);
    formData.append("track_b", trackB);

    try {
      const response = await fetch(`${this.baseUrl}${ANALYZE_ENDPOINT}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(FRIENDLY_ERROR_MESSAGE);
      }

      return (await response.json()) as UploadAnalysisResponse;
    } catch {
      throw new Error(FRIENDLY_ERROR_MESSAGE);
    }
  }
}

export const apiService = new ApiService();
