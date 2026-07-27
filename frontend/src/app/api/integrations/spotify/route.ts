import { createHmac } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "@/lib/auth";

const BACKEND_URL = (process.env.BACKEND_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

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

  if (action === "status") {
    const response = await fetch(
      `${BACKEND_URL}/api/v1/integrations/spotify/status`,
      { headers: { ...getAuthHeaders(session.user.id) }, cache: "no-store" },
    );
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  }

  if (action === "connect") {
    const response = await fetch(
      `${BACKEND_URL}/api/v1/integrations/spotify/connect`,
      { headers: { ...getAuthHeaders(session.user.id) }, cache: "no-store" },
    );
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  }

  return NextResponse.json({ detail: "Unknown action" }, { status: 400 });
}

export async function DELETE() {
  const session = await getServerSession();
  if (!session?.user) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const response = await fetch(
    `${BACKEND_URL}/api/v1/integrations/spotify/`,
    {
      method: "DELETE",
      headers: { ...getAuthHeaders(session.user.id) },
    },
  );

  if (response.status === 204) {
    return new NextResponse(null, { status: 204 });
  }

  const body = await response.json().catch(() => ({}));
  return NextResponse.json(body, { status: response.status });
}
