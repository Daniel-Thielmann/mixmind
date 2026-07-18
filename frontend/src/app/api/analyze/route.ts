import { createHmac } from "node:crypto";
import { headers } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session?.user?.id) {
    return NextResponse.json(
      { detail: "You must sign in before running an analysis." },
      { status: 401 },
    );
  }

  const userId = session.user.id;
  const secret = process.env.INTERNAL_AUTH_SECRET?.trim() ?? "";
  if (!secret) {
    return NextResponse.json(
      { detail: "Analysis integration is not configured." },
      { status: 503 },
    );
  }
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = createHmac("sha256", secret)
    .update(`${userId}:${timestamp}`)
    .digest("hex");
  const apiUrl = (process.env.BACKEND_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
  const formData = await request.formData();
  const response = await fetch(`${apiUrl}/api/v1/analysis/analyze`, {
    method: "POST",
    headers: {
      "X-MixMind-User": userId,
      "X-MixMind-Timestamp": timestamp,
      "X-MixMind-Signature": signature,
    },
    body: formData,
  });
  const body = await response.json().catch(() => ({ detail: "Invalid backend response" }));
  return NextResponse.json(body, { status: response.status });
}
