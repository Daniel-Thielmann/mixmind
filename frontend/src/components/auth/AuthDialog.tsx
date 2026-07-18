"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
import { SpotifyButton } from "./SpotifyButton";

interface AuthDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
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

export function AuthDialog({ open, onOpenChange }: AuthDialogProps) {
  const { signInGoogle, signInGithub, signInSpotify } = useAuth();
  const [loading, setLoading] = useState<"google" | "github" | "spotify" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const signInFns = {
    google: signInGoogle,
    github: signInGithub,
    spotify: signInSpotify,
  } as const;

  const handleSignIn = async (provider: keyof typeof signInFns) => {
    setLoading(provider);
    setError(null);
    try {
      await signInFns[provider]();
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
                <div className="relative my-1">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border/50" />
                  </div>
                  <div className="relative flex justify-center text-xs">
                    <span className="bg-card/80 px-2 text-text-tertiary">Import your library</span>
                  </div>
                </div>
                <SpotifyButton
                  loading={loading === "spotify"}
                  onClick={() => handleSignIn("spotify")}
                />
                {error ? (
                  <p role="alert" className="rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-red-200">
                    {error}
                  </p>
                ) : null}
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
