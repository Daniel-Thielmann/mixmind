import { createHmac } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "@/lib/auth";

export const runtime = "nodejs";
export const maxDuration = 300;

export async function POST(request: NextRequest) {
  const session = await getServerSession();
  if (!session?.user?.id) return NextResponse.json({ detail: "Authentication required." }, { status: 401 });
  const secret = process.env.INTERNAL_AUTH_SECRET?.trim() ?? "";
  if (!secret) return NextResponse.json({ detail: "Integration is not configured." }, { status: 503 });
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = createHmac("sha256", secret).update(`${session.user.id}:${timestamp}`).digest("hex");
  const backend = (process.env.BACKEND_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
  try {
    const response = await fetch(`${backend}/api/v1/youtube/analyze/stream`, { method: "POST", headers: { "Content-Type": "application/json", "X-MixMind-User": session.user.id, "X-MixMind-Timestamp": timestamp, "X-MixMind-Signature": signature }, body: JSON.stringify(await request.json()), signal: AbortSignal.timeout(Number(process.env.BACKEND_ANALYSIS_TIMEOUT_MS ?? 120000)) });
    if (!response.ok || !response.body) {
      return NextResponse.json(await response.json().catch(() => ({ detail: "YouTube analysis failed." })), { status: response.status });
    }
    return new Response(response.body, {
      status: response.status,
      headers: {
        "Content-Type": "application/x-ndjson",
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
      },
    });
  } catch {
    return NextResponse.json({ detail: "YouTube analysis timed out or is unavailable." }, { status: 504 });
  }
}
