import { createHmac } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "@/lib/auth";

export const runtime = "nodejs";

const BACKEND_URL = (
  process.env.BACKEND_API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

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
  const session = await getServerSession();
  if (!session?.user) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const action = searchParams.get("action");

  if (action === "playlists") {
    const limit = searchParams.get("limit") ?? "20";
    const offset = searchParams.get("offset") ?? "0";
    const response = await fetch(
      `${BACKEND_URL}/api/v1/integrations/spotify/playlists?limit=${limit}&offset=${offset}`,
      { headers: { ...getAuthHeaders(session.user.id) }, cache: "no-store" },
    );
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  }

  if (action === "playlist-tracks") {
    const playlistId = searchParams.get("playlist_id");
    const limit = searchParams.get("limit") ?? "50";
    const offset = searchParams.get("offset") ?? "0";
    if (!playlistId) {
      return NextResponse.json({ detail: "Missing playlist_id" }, { status: 400 });
    }
    const response = await fetch(
      `${BACKEND_URL}/api/v1/integrations/spotify/playlists/${playlistId}/tracks?limit=${limit}&offset=${offset}`,
      { headers: { ...getAuthHeaders(session.user.id) }, cache: "no-store" },
    );
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  }

  if (action === "saved-tracks") {
    const limit = searchParams.get("limit") ?? "20";
    const offset = searchParams.get("offset") ?? "0";
    const response = await fetch(
      `${BACKEND_URL}/api/v1/integrations/spotify/saved-tracks?limit=${limit}&offset=${offset}`,
      { headers: { ...getAuthHeaders(session.user.id) }, cache: "no-store" },
    );
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  }

  if (action === "search") {
    const q = searchParams.get("q");
    const limit = searchParams.get("limit") ?? "10";
    const offset = searchParams.get("offset") ?? "0";
    if (!q) {
      return NextResponse.json({ detail: "Missing search query" }, { status: 400 });
    }
    const response = await fetch(
      `${BACKEND_URL}/api/v1/integrations/spotify/search?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`,
      { headers: { ...getAuthHeaders(session.user.id) }, cache: "no-store" },
    );
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  }

  return NextResponse.json({ detail: "Unknown action" }, { status: 400 });
}
