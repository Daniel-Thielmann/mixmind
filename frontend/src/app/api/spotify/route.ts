import { createHmac } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "@/lib/auth";

export const runtime = "nodejs";

const BACKEND_URL = (
  process.env.BACKEND_API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

const FETCH_TIMEOUT_MS = parseInt(
  process.env.BACKEND_FETCH_TIMEOUT_MS ?? "25000",
  10,
);

const SPOTIFY_TIMEOUT_MS = parseInt(
  process.env.BACKEND_SPOTIFY_TIMEOUT_MS ?? "35000",
  10,
);

function getAuthHeaders(userId: string): Record<string, string> {
  const secret = process.env.INTERNAL_AUTH_SECRET?.trim();
  if (!secret) return {};
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = createHmac("sha256", secret)
    .update(`${userId}:${timestamp}`)
    .digest("hex");
  return {
    "X-MixMind-User": userId,
    "X-MixMind-Timestamp": timestamp,
    "X-MixMind-Signature": signature,
  };
}

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession();
    if (!session?.user) {
      return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const action = searchParams.get("action");

    if (!action) {
      return NextResponse.json({ detail: "Missing action parameter" }, { status: 400 });
    }

    const headers = { ...getAuthHeaders(session.user.id), "Content-Type": "application/json" };

    if (action === "playlists") {
      const limit = searchParams.get("limit") ?? "20";
      const offset = searchParams.get("offset") ?? "0";
      return await proxyToBackend(
        `${BACKEND_URL}/api/v1/integrations/spotify/playlists?limit=${limit}&offset=${offset}`,
        headers,
        "playlists",
      );
    }

    if (action === "playlist-tracks") {
      const playlistId = searchParams.get("playlist_id");
      const limit = searchParams.get("limit") ?? "50";
      const offset = searchParams.get("offset") ?? "0";
      if (!playlistId) {
        return NextResponse.json({ detail: "Missing playlist_id" }, { status: 400 });
      }
      return await proxyToBackend(
        `${BACKEND_URL}/api/v1/integrations/spotify/playlists/${encodeURIComponent(playlistId)}/tracks?limit=${limit}&offset=${offset}`,
        headers,
        "playlist-tracks",
      );
    }

    if (action === "saved-tracks") {
      const limit = searchParams.get("limit") ?? "20";
      const offset = searchParams.get("offset") ?? "0";
      return await proxyToBackend(
        `${BACKEND_URL}/api/v1/integrations/spotify/saved-tracks?limit=${limit}&offset=${offset}`,
        headers,
        "saved-tracks",
      );
    }

    if (action === "search") {
      const q = searchParams.get("q");
      const rawLimit = searchParams.get("limit") ?? "10";
      const offset = searchParams.get("offset") ?? "0";
      if (!q || !q.trim()) {
        return NextResponse.json({ detail: "Missing search query" }, { status: 400 });
      }
      const limit = Math.min(Math.max(parseInt(rawLimit, 10) || 10, 1), 10);
      const url = new URL(`${BACKEND_URL}/api/v1/integrations/spotify/search`);
      url.searchParams.set("q", q.trim());
      url.searchParams.set("limit", String(limit));
      url.searchParams.set("offset", String(Math.max(parseInt(offset, 10) || 0, 0)));
      return await proxyToBackend(url.toString(), headers, "search");
    }

    return NextResponse.json({ detail: `Unknown action: ${action}` }, { status: 400 });
  } catch (error) {
    console.error("Spotify BFF error:", error);
    return NextResponse.json(
      { detail: "Failed to proxy request to backend" },
      { status: 502 },
    );
  }
}

async function proxyToBackend(
  url: string,
  headers: Record<string, string>,
  action: string,
): Promise<NextResponse> {
  const timeoutMs = action === "search" ? FETCH_TIMEOUT_MS : SPOTIFY_TIMEOUT_MS;
  const startedAt = performance.now();

  let response: Response;
  try {
    response = await fetch(url, {
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (err) {
    const elapsed = Math.round(performance.now() - startedAt);
    const urlPath = new URL(url).pathname;
    console.error("Backend fetch failed:", { action, urlPath, elapsed, err });

    let detail: string;
    let status: number;

    if (err instanceof DOMException && ["AbortError", "TimeoutError"].includes(err.name)) {
      detail = "Spotify took too long to respond. Please try again.";
      status = 504;
    } else if (err instanceof TypeError && (err.message.includes("fetch") || err.message.includes("network"))) {
      detail = "MixMind backend is temporarily unavailable.";
      status = 502;
    } else if (err instanceof TypeError && (err.message.includes("econnrefused") || err.message.includes("ECONNREFUSED"))) {
      detail = "MixMind backend is temporarily unavailable.";
      status = 502;
    } else {
      detail = "MixMind backend is temporarily unavailable.";
      status = 502;
    }

    return NextResponse.json(
      {
        detail,
        error_type:
          status === 504
            ? "spotify_timeout"
            : "backend_unavailable",
      },
      { status },
    );
  }

  console.info("Spotify BFF request completed", {
    action,
    status: response.status,
    elapsed: Math.round(performance.now() - startedAt),
  });

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    const text = await response.text().catch(() => "");
    console.error("Backend returned non-JSON response:", response.status, text.slice(0, 500));
    return NextResponse.json(
      { detail: "Backend returned an invalid response." },
      { status: 502 },
    );
  }

  return NextResponse.json(body, { status: response.status });
}
