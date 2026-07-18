import { createHmac } from "node:crypto";
import { headers } from "next/headers";
import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function GET() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session?.user) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const secret = process.env.INTERNAL_AUTH_SECRET?.trim();
  if (!secret) {
    return NextResponse.json({ detail: "Dashboard integration is not configured" }, { status: 503 });
  }

  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = createHmac("sha256", secret)
    .update(`${session.user.id}:${timestamp}`)
    .digest("hex");
  const apiUrl = (process.env.BACKEND_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
  const response = await fetch(`${apiUrl}/api/v1/tracks/dashboard`, {
    headers: {
      "X-MixMind-User": session.user.id,
      "X-MixMind-Timestamp": timestamp,
      "X-MixMind-Signature": signature,
    },
    cache: "no-store",
  });
  const body = await response.json().catch(() => ({ detail: "Invalid backend response" }));
  return NextResponse.json(body, { status: response.status });
}
