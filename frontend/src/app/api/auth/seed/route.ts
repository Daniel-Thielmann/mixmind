import { NextResponse } from "next/server";

export async function POST() {
  const baseUrl = process.env.BETTER_AUTH_URL ?? "http://127.0.0.1:3000";

  const res = await fetch(`${baseUrl}/api/auth/sign-up/email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: "Admin",
      email: "admin@admin",
      password: "admin123",
    }),
  });

  const body = await res.json().catch(() => ({}));
  const msg = String(body?.error ?? body?.message ?? "");

  if (res.ok) {
    return NextResponse.json({ message: "Admin created" });
  }
  if (msg.toLowerCase().includes("already exists")) {
    return NextResponse.json({ message: "Admin already exists" });
  }
  return NextResponse.json({ error: msg || "Sign-up failed", status: res.status }, { status: 400 });
}
