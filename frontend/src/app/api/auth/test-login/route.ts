import { createHmac } from "node:crypto";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const ADMIN_EMAIL = "admin@admin";
const ADMIN_PASSWORD = "admin123";
const ADMIN_ID = "00000000-0000-0000-0000-000000000001";

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();
    if (!email || !password) {
      return NextResponse.json({ error: "Email and password required" }, { status: 400 });
    }
    if (email !== ADMIN_EMAIL || password !== ADMIN_PASSWORD) {
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
    }

    const secret = process.env.INTERNAL_AUTH_SECRET?.trim() || "insecure-dev-secret";
    const timestamp = Math.floor(Date.now() / 1000).toString();
    const signature = createHmac("sha256", secret)
      .update(`${ADMIN_ID}:${timestamp}`)
      .digest("hex");

    const userPayload = {
      id: ADMIN_ID,
      email: ADMIN_EMAIL,
      name: "Admin",
      image: null,
      plan: "FREE",
      aiCreditsUsed: 0,
      aiCreditsLimit: 500,
    };

    const cookie = {
      user: userPayload,
      auth: { userId: ADMIN_ID, timestamp, signature },
    };
    const encoded = Buffer.from(JSON.stringify(cookie)).toString("base64");

    const cookieStore = await cookies();
    cookieStore.set("mixmind_admin_session", encoded, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });

    return NextResponse.json({ user: userPayload, auth: { userId: ADMIN_ID, timestamp, signature } });
  } catch {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}
