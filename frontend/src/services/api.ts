import type {
  AnalysisProgressEvent,
  UploadAnalysisResponse,
} from "@/types";

const ANALYZE_AUTHORIZATION_ENDPOINT = "/api/analyze/authorize";
const FRIENDLY_ERROR_MESSAGE =
  "Unable to analyze the selected tracks. Please try again.";
export const AUTH_REQUIRED_MESSAGE =
  "You need to sign in before running an analysis.";

export class ApiService {
  constructor(private readonly baseUrl = "") {}

  async analyzeTracks(
    trackA: File,
    trackB: File,
    onProgress?: (event: AnalysisProgressEvent) => void,
  ): Promise<UploadAnalysisResponse> {
    const formData = new FormData();
    formData.append("track_a", trackA);
    formData.append("track_b", trackB);

    try {
      const authorizationResponse = await fetch(
        `${this.baseUrl}${ANALYZE_AUTHORIZATION_ENDPOINT}`,
        { method: "POST" },
      );
      if (!authorizationResponse.ok) {
        if (authorizationResponse.status === 401) {
          throw new Error(AUTH_REQUIRED_MESSAGE);
        }
        const payload = (await authorizationResponse.json().catch(() => null)) as
          | { detail?: string }
          | null;
        throw new Error(payload?.detail ?? FRIENDLY_ERROR_MESSAGE);
      }

      const authorization = (await authorizationResponse.json()) as {
        uploadUrl: string;
        streamUrl: string;
        headers: Record<string, string>;
      };
      const response = await fetch(authorization.streamUrl, {
        method: "POST",
        headers: authorization.headers,
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error(AUTH_REQUIRED_MESSAGE);
        }

        const payload = (await response.json().catch(() => null)) as
          | { detail?: string }
          | null;
        throw new Error(payload?.detail ?? FRIENDLY_ERROR_MESSAGE);
      }

      return readAnalysisStream(response, onProgress);
    } catch (error) {
      throw error instanceof Error ? error : new Error(FRIENDLY_ERROR_MESSAGE);
    }
  }
}

export const apiService = new ApiService();

export async function readAnalysisStream(
  response: Response,
  onProgress?: (event: AnalysisProgressEvent) => void,
): Promise<UploadAnalysisResponse> {
  if (!response.body) {
    throw new Error("Progressive analysis is unavailable in this browser.");
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  let result: UploadAnalysisResponse | null = null;

  const consumeLine = (line: string) => {
    if (!line.trim()) return;
    const event = JSON.parse(line) as AnalysisProgressEvent;
    onProgress?.(event);
    if (event.stage === "failed") {
      throw new Error(event.message || FRIENDLY_ERROR_MESSAGE);
    }
    if (event.stage === "completed") {
      result = event.data as UploadAnalysisResponse;
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    lines.forEach(consumeLine);
  }
  consumeLine(buffer);

  if (!result) {
    throw new Error("The analysis stream ended before producing a result.");
  }
  return result;
}
