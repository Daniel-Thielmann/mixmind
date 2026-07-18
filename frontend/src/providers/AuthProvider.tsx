"use client";

import { createContext, useCallback, useEffect, useState } from "react";
import { authClient } from "@/lib/auth-client";
import type { AuthUser } from "@/types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  signInGoogle: () => Promise<void>;
  signInGithub: () => Promise<void>;
  signInSpotify: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

function mapSessionToUser(session: {
  user: {
    id: string;
    name: string;
    email: string;
    image?: string | null;
    plan?: string | null;
    aiCreditsUsed?: number | null;
    aiCreditsLimit?: number | null;
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

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
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
    const timeoutId = window.setTimeout(() => void refreshUser(), 0);
    return () => window.clearTimeout(timeoutId);
  }, [refreshUser]);

  const signInGoogle = useCallback(async () => {
    const { error } = await authClient.signIn.social({
      provider: "google",
      callbackURL: "/dashboard",
    });
    if (error) throw new Error(error.message ?? "Google sign-in failed.");
  }, []);

  const signInGithub = useCallback(async () => {
    const { error } = await authClient.signIn.social({
      provider: "github",
      callbackURL: "/dashboard",
    });
    if (error) throw new Error(error.message ?? "GitHub sign-in failed.");
  }, []);

  const signInSpotify = useCallback(async () => {
    const { error } = await authClient.signIn.social({
      provider: "spotify",
      callbackURL: "/dashboard",
    });
    if (error) throw new Error(error.message ?? "Spotify sign-in failed.");
  }, []);

  const logout = useCallback(async () => {
    await authClient.signOut();
    setUser(null);
  }, []);

  const value: AuthContextValue = {
    user,
    loading,
    isAuthenticated: !!user,
    signInGoogle,
    signInGithub,
    signInSpotify,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
