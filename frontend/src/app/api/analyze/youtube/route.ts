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
    const response = await fetch(`${backend}/api/v1/youtube/analyze`, { method: "POST", headers: { "Content-Type": "application/json", "X-MixMind-User": session.user.id, "X-MixMind-Timestamp": timestamp, "X-MixMind-Signature": signature }, body: JSON.stringify(await request.json()), signal: AbortSignal.timeout(Number(process.env.BACKEND_ANALYSIS_TIMEOUT_MS ?? 120000)) });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "YouTube analysis timed out or is unavailable." }, { status: 504 });
  }
}
