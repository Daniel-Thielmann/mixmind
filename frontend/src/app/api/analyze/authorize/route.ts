import { createHmac } from "node:crypto";
import { NextResponse } from "next/server";
import { getServerSession } from "@/lib/auth";

export const runtime = "nodejs";

export async function POST() {
  const session = await getServerSession();
  if (!session?.user?.id) {
    return NextResponse.json(
      { detail: "You must sign in before running an analysis." },
      { status: 401 },
    );
  }

  const secret = process.env.INTERNAL_AUTH_SECRET?.trim();
  if (!secret) {
    return NextResponse.json(
      { detail: "Analysis integration is not configured." },
      { status: 503 },
    );
  }

  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = createHmac("sha256", secret)
    .update(`${session.user.id}:${timestamp}:analysis`)
    .digest("hex");
  const apiUrl = (
    process.env.BACKEND_API_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000"
  ).replace(/\/$/, "");

  return NextResponse.json(
    {
      uploadUrl: `${apiUrl}/api/v1/analysis/analyze`,
      streamUrl: `${apiUrl}/api/v1/analysis/analyze/stream`,
      headers: {
        "X-MixMind-User": session.user.id,
        "X-MixMind-Timestamp": timestamp,
        "X-MixMind-Signature": signature,
        "X-MixMind-Scope": "analysis",
      },
    },
    { headers: { "Cache-Control": "no-store" } },
  );
}
