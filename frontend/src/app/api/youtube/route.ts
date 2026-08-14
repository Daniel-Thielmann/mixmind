import { createHmac } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

import { getServerSession } from "@/lib/auth";

interface ApiItem {
  id?: { videoId?: string };
  snippet?: { title?: string; channelTitle?: string; thumbnails?: { medium?: { url?: string }; default?: { url?: string } } };
}

export async function GET(request: NextRequest) {
  const session = await getServerSession();
  if (!session?.user?.id) return NextResponse.json({ detail: "Authentication required." }, { status: 401 });
  const secret = process.env.INTERNAL_AUTH_SECRET?.trim() ?? "";
  if (!secret) return NextResponse.json({ detail: "Integration is not configured." }, { status: 503 });
  const query = request.nextUrl.searchParams.get("q") ?? "";
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = createHmac("sha256", secret).update(`${session.user.id}:${timestamp}`).digest("hex");
  const backend = (process.env.BACKEND_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
  const response = await fetch(`${backend}/api/v1/youtube/search?q=${encodeURIComponent(query)}`, { headers: { "X-MixMind-User": session.user.id, "X-MixMind-Timestamp": timestamp, "X-MixMind-Signature": signature }, cache: "no-store" });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) return NextResponse.json(body, { status: response.status });
  const items = (body.items ?? []).map((item: ApiItem) => ({ id: item.id?.videoId, title: item.snippet?.title, channel: item.snippet?.channelTitle, thumbnail: item.snippet?.thumbnails?.medium?.url ?? item.snippet?.thumbnails?.default?.url })).filter((item: { id?: string }) => item.id);
  return NextResponse.json({ items, nextPageToken: body.nextPageToken ?? null });
}
