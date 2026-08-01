"use client";

import { createContext, useCallback, useEffect, useState } from "react";
import { authClient } from "@/lib/auth-client";
import type { AuthUser } from "@/types/auth";
import { safeReturnTo } from "@/lib/safe-return-to";

const ADMIN_STORAGE_KEY = "mixmind_admin_session";

interface AdminSession {
  user: AuthUser;
  auth: { userId: string; timestamp: string; signature: string };
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  signInGoogle: (returnTo?: string) => Promise<void>;
  signInGithub: (returnTo?: string) => Promise<void>;
  signInEmail: (email: string, password: string) => Promise<string | null>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  getAuthHeaders: () => Record<string, string> | null;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

function mapSessionToUser(session: {
  user: {
    id: string; name: string; email: string;
    image?: string | null; plan?: string | null;
    aiCreditsUsed?: number | null; aiCreditsLimit?: number | null;
  } | null;
}): AuthUser | null {
  if (!session.user) return null;
  const plan = (session.user.plan ?? "FREE") as AuthUser["plan"];
  return {
    id: session.user.id,
    name: session.user.name,
    email: session.user.email,
    image: session.user.image,
    plan: ["FREE", "PRO", "ENTERPRISE"].includes(plan) ? plan : "FREE",
    aiCreditsUsed: session.user.aiCreditsUsed ?? 0,
    aiCreditsLimit: session.user.aiCreditsLimit ?? 500,
  };
}

function loadAdminSession(): AdminSession | null {
  try {
    const raw = sessionStorage.getItem(ADMIN_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AdminSession) : null;
  } catch { return null; }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [adminSession, setAdminSession] = useState<AdminSession | null>(null);

  const refreshUser = useCallback(async () => {
    const admin = loadAdminSession();
    if (admin) {
      setAdminSession(admin);
      setUser(admin.user);
      setLoading(false);
      return;
    }
    try {
      const { data } = await authClient.getSession();
      setUser(mapSessionToUser({ user: data?.user ?? null }));
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const t = window.setTimeout(() => void refreshUser(), 0);
    return () => window.clearTimeout(t);
  }, [refreshUser]);

  const signInGoogle = useCallback(async (returnTo?: string) => {
    const { error } = await authClient.signIn.social({
      provider: "google", callbackURL: safeReturnTo(returnTo),
    });
    if (error) throw new Error(error.message ?? "Google sign-in failed.");
  }, []);

  const signInGithub = useCallback(async (returnTo?: string) => {
    const { error } = await authClient.signIn.social({
      provider: "github", callbackURL: safeReturnTo(returnTo),
    });
    if (error) throw new Error(error.message ?? "GitHub sign-in failed.");
  }, []);

  const signInEmail = useCallback(async (email: string, password: string) => {
    const res = await fetch("/api/auth/test-login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const body = await res.json();
    if (!res.ok) return body.error ?? "Sign-in failed.";

    const session: AdminSession = { user: body.user, auth: body.auth };
    sessionStorage.setItem(ADMIN_STORAGE_KEY, JSON.stringify(session));
    setAdminSession(session);
    setUser(body.user);
    return null;
  }, []);

  const logout = useCallback(async () => {
    sessionStorage.removeItem(ADMIN_STORAGE_KEY);
    setAdminSession(null);
    await authClient.signOut();
    setUser(null);
    await fetch("/api/auth/test-login/clear", { method: "POST" }).catch(() => {});
  }, []);

  const getAuthHeaders = useCallback(() => {
    if (adminSession) {
      return {
        "X-MixMind-User": adminSession.auth.userId,
        "X-MixMind-Timestamp": adminSession.auth.timestamp,
        "X-MixMind-Signature": adminSession.auth.signature,
      };
    }
    return null;
  }, [adminSession]);

  return (
    <AuthContext.Provider
      value={{
        user, loading, isAuthenticated: !!user,
        signInGoogle, signInGithub, signInEmail,
        logout, refreshUser, getAuthHeaders,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
