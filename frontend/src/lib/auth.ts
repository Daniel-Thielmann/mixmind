import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { Pool } from "pg";
import { createHmac } from "node:crypto";
import { cookies, headers } from "next/headers";
import { db } from "@/lib/db";
import * as schema from "@/db/schema";

const databaseUrl = process.env.DATABASE_URL?.trim();

const database = databaseUrl
  ? new Pool({
      connectionString: databaseUrl,
      ssl:
        process.env.NODE_ENV === "production"
          ? { rejectUnauthorized: false }
          : undefined,
      max: 5,
    })
  : drizzleAdapter(db, {
      provider: "sqlite",
      schema: {
        user: schema.user,
        session: schema.session,
        account: schema.account,
        verification: schema.verification,
      },
    });

export const auth = betterAuth({
  baseURL: process.env.BETTER_AUTH_URL ?? "http://127.0.0.1:3000",
  secret: process.env.BETTER_AUTH_SECRET,
  trustedOrigins: [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "https://*.mixmind.app",
    process.env.BETTER_AUTH_URL,
  ].filter(Boolean) as string[],
  database,
  emailAndPassword: {
    enabled: true,
    autoSignIn: true,
    async sendResetPassword() {},
  },
  user: {
    additionalFields: {
      plan: {
        type: "string",
        required: false,
        defaultValue: "FREE",
        input: false,
      },
      aiCreditsUsed: {
        type: "number",
        required: false,
        defaultValue: 0,
        input: false,
      },
      aiCreditsLimit: {
        type: "number",
        required: false,
        defaultValue: 500,
        input: false,
      },
    },
  },
  socialProviders: {
    ...(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET
      ? { google: { clientId: process.env.GOOGLE_CLIENT_ID, clientSecret: process.env.GOOGLE_CLIENT_SECRET } }
      : {}),
    ...(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET
      ? { github: { clientId: process.env.GITHUB_CLIENT_ID, clientSecret: process.env.GITHUB_CLIENT_SECRET } }
      : {}),
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7,
    updateAge: 60 * 60 * 24,
  },
});

interface AdminSessionUser {
  id: string; name: string; email: string; image: string | null;
  plan: string; aiCreditsUsed: number; aiCreditsLimit: number;
}

export async function getServerSession() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (session?.user) return session;

  const cookieStore = await cookies();
  const raw = cookieStore.get("mixmind_admin_session")?.value;
  if (!raw) return null;

  try {
    const decoded = JSON.parse(Buffer.from(raw, "base64").toString("utf-8")) as {
      user: AdminSessionUser;
      auth: { userId: string; timestamp: string; signature: string };
    };
    const secret = process.env.INTERNAL_AUTH_SECRET?.trim() || "insecure-dev-secret";
    const expected = createHmac("sha256", secret)
      .update(`${decoded.auth.userId}:${decoded.auth.timestamp}`)
      .digest("hex");
    if (expected !== decoded.auth.signature) return null;
    return { user: decoded.user };
  } catch {
    return null;
  }
}
