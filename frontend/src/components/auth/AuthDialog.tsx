"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { GoogleButton } from "./GoogleButton";
import { GitHubButton } from "./GitHubButton";
import { Mail, Lock, Loader2 } from "lucide-react";
import { safeReturnTo } from "@/lib/safe-return-to";

interface AuthDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  returnTo?: string;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { y: 12, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] as const },
  },
};

export function AuthDialog({ open, onOpenChange, returnTo }: AuthDialogProps) {
  const { signInGoogle, signInGithub, signInEmail } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState<"google" | "github" | "email" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [seeding, setSeeding] = useState(false);

  const signInFns = {
    google: signInGoogle,
    github: signInGithub,
  } as const;

  const handleSignIn = async (provider: keyof typeof signInFns) => {
    setLoading(provider);
    setError(null);
    try {
      await signInFns[provider](safeReturnTo(returnTo));
    } catch (signInError) {
      setError(
        signInError instanceof Error
          ? signInError.message
          : "Sign-in is unavailable. Check the provider configuration.",
      );
    } finally {
      setLoading(null);
    }
  };

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading("email");
    setError(null);
    if (!seeding) {
      setSeeding(true);
      try {
        await fetch("/api/auth/seed", { method: "POST" });
      } catch { /* ignore seed errors */ }
    }
    try {
      const err = await signInEmail(email.trim(), password);
      if (err) {
        setError(err);
        setLoading(null);
        return;
      }
      onOpenChange(false);
      router.push(safeReturnTo(returnTo));
    } catch (signInError) {
      setError(
        signInError instanceof Error
          ? signInError.message
          : "Sign-in failed.",
      );
    } finally {
      setLoading(null);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <Dialog open={open} onOpenChange={onOpenChange}>
          <DialogContent className="sm:max-w-sm">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="flex flex-col items-center gap-6 py-4"
            >
              <motion.div variants={itemVariants}>
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-primary-dark text-xl font-bold text-background shadow-lg shadow-primary/20">
                  M
                </div>
              </motion.div>

              <motion.div variants={itemVariants}>
                <DialogHeader className="text-center">
                  <DialogTitle className="text-xl">Continue to MixMind</DialogTitle>
                  <DialogDescription className="text-balance pt-1">
                    Use your favorite provider to continue.
                  </DialogDescription>
                </DialogHeader>
              </motion.div>

              <motion.div variants={itemVariants} className="flex w-full flex-col gap-3">
                <GoogleButton
                  loading={loading === "google"}
                  onClick={() => handleSignIn("google")}
                />
                <GitHubButton
                  loading={loading === "github"}
                  onClick={() => handleSignIn("github")}
                />

                {error ? (
                  <p role="alert" className="rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-red-200">
                    {error}
                  </p>
                ) : null}
              </motion.div>

              <motion.div variants={itemVariants} className="w-full">
                <div className="relative my-2">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border/50" />
                  </div>
                  <div className="relative flex justify-center text-xs">
                    <span className="bg-card px-2 text-text-tertiary">or continue with email</span>
                  </div>
                </div>
                <form onSubmit={handleEmailSignIn} className="flex flex-col gap-3">
                  <div className="relative">
                    <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
                    <input
                      type="email"
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full rounded-lg border border-border/50 bg-background/50 py-2.5 pl-10 pr-3 text-sm text-text placeholder:text-text-tertiary focus:border-primary/50 focus:outline-hidden"
                      required
                    />
                  </div>
                  <div className="relative">
                    <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
                    <input
                      type="password"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full rounded-lg border border-border/50 bg-background/50 py-2.5 pl-10 pr-3 text-sm text-text placeholder:text-text-tertiary focus:border-primary/50 focus:outline-hidden"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading === "email"}
                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-50"
                  >
                    {loading === "email" ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : null}
                    Sign in with Email
                  </button>
                </form>
              </motion.div>

              <motion.p
                variants={itemVariants}
                className="text-center text-xs text-text-tertiary"
              >
                By continuing, you agree to MixMind&apos;s{" "}
                <a href="#" className="underline underline-offset-2 hover:text-text-secondary transition-colors">
                  Terms
                </a>{" "}
                and{" "}
                <a href="#" className="underline underline-offset-2 hover:text-text-secondary transition-colors">
                  Privacy Policy
                </a>
                .
              </motion.p>
            </motion.div>
          </DialogContent>
        </Dialog>
      )}
    </AnimatePresence>
  );
}
