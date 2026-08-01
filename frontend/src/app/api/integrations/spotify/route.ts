import { createHmac } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "@/lib/auth";

const BACKEND_URL = (process.env.BACKEND_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

const FETCH_TIMEOUT_MS = parseInt(
  process.env.BACKEND_FETCH_TIMEOUT_MS ?? "25000",
  10,
);

const STATUS_TIMEOUT_MS = parseInt(
  process.env.BACKEND_STATUS_TIMEOUT_MS ?? "10000",
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

    const headers = { ...getAuthHeaders(session.user.id), "Content-Type": "application/json" };

    if (action === "status") {
      return await proxyToBackend(`${BACKEND_URL}/api/v1/integrations/spotify/status`, headers, "status");
    }

    if (action === "connect") {
      const returnTo = searchParams.get("return_to") ?? "/dashboard/settings/integrations";
      const url = new URL(`${BACKEND_URL}/api/v1/integrations/spotify/connect`);
      url.searchParams.set("return_to", returnTo);
      return await proxyToBackend(url.toString(), headers, "connect");
    }

    return NextResponse.json({ detail: `Unknown action: ${action}` }, { status: 400 });
  } catch (error) {
    console.error("Integrations Spotify BFF error:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE() {
  try {
    const session = await getServerSession();
    if (!session?.user) {
      return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
    }

    const response = await fetch(
      `${BACKEND_URL}/api/v1/integrations/spotify/`,
      {
        method: "DELETE",
        headers: { ...getAuthHeaders(session.user.id) },
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
      },
    );

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const body = await response.json().catch(() => ({}));
    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    console.error("Spotify disconnect error:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

async function proxyToBackend(
  url: string,
  headers: Record<string, string>,
  action: string,
): Promise<NextResponse> {
  const timeoutMs = action === "status" ? STATUS_TIMEOUT_MS : FETCH_TIMEOUT_MS;
  const startedAt = performance.now();

  let response: Response;
  try {
    response = await fetch(url, { headers, cache: "no-store", signal: AbortSignal.timeout(timeoutMs) });
  } catch (err) {
    const urlPath = new URL(url).pathname;
    console.error("Backend fetch failed:", {
      action,
      urlPath,
      elapsed: Math.round(performance.now() - startedAt),
      err,
    });

    let detail: string;
    let status: number;

    if (err instanceof DOMException && ["AbortError", "TimeoutError"].includes(err.name)) {
      detail = "Spotify took too long to respond. Please try again.";
      status = 504;
    } else if (err instanceof TypeError && (err.message.includes("econnrefused") || err.message.includes("ECONNREFUSED"))) {
      detail = "MixMind backend is temporarily unavailable.";
      status = 502;
    } else {
      detail = "MixMind backend is temporarily unavailable.";
      status = 502;
    }

    return NextResponse.json({ detail, error_type: status === 504 ? "spotify_timeout" : "backend_unavailable" }, { status });
  }


  console.info("Spotify integration BFF request completed", {
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
    return NextResponse.json({ detail: "Backend returned an invalid response." }, { status: 502 });
  }

  return NextResponse.json(body, { status: response.status });
}
