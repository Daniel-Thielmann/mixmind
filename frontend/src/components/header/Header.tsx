"use client";

import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Menu,
  X,
  LayoutDashboard,
  Sparkles,
  DollarSign,
  AudioLines,
  CirclePlay,
  Workflow,
  BrainCircuit,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { AuthDialog } from "@/components/auth/AuthDialog";
import { UserDropdown } from "@/components/auth/UserDropdown";

const NAV_LINKS = [
  { label: "Demo", href: "/#demo", sectionId: "demo", icon: CirclePlay },
  {
    label: "How It Works",
    href: "/#how-it-works",
    sectionId: "how-it-works",
    icon: Workflow,
  },
  {
    label: "AI Recommendation",
    href: "/#ai-recommendation",
    sectionId: "ai-recommendation",
    icon: BrainCircuit,
  },
  { label: "Features", href: "/#features", sectionId: "features", icon: Sparkles },
  { label: "Analyzer", href: "/#analyzer", sectionId: "analyzer", icon: AudioLines },
  { label: "Pricing", href: "/#pricing", sectionId: "pricing", icon: DollarSign },
];

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const { isAuthenticated, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (pathname !== "/") {
      return;
    }

    const sections = NAV_LINKS.map((link) =>
      document.getElementById(link.sectionId),
    ).filter((section): section is HTMLElement => section !== null);

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (visible) setActiveSection(visible.target.id);
      },
      { rootMargin: "-20% 0px -65%", threshold: [0, 0.1, 0.25, 0.5] },
    );

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, [pathname]);

  const navigateTo = (sectionId: string) => {
    setMobileOpen(false);

    if (pathname !== "/") {
      router.push(`/#${sectionId}`);
      return;
    }

    const section = document.getElementById(sectionId);
    if (!section) return;

    const headerOffset = 80;
    const targetTop = section.getBoundingClientRect().top + window.scrollY - headerOffset;
    window.history.replaceState(null, "", `#${sectionId}`);
    window.scrollTo({ top: targetTop, behavior: "smooth" });
    setActiveSection(sectionId);
  };

  const isActive = (sectionId: string) => {
    return pathname === "/" && activeSection === sectionId;
  };

  return (
    <>
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] as const }}
        className="fixed inset-x-0 top-0 z-50"
      >
        <div
          className={`relative transition-all duration-500 ${
            scrolled
              ? "border-b border-border/50 bg-background/70 backdrop-blur-2xl"
              : "bg-transparent"
          }`}
        >
          <div
            className={`absolute inset-x-0 top-0 h-px bg-linear-to-r from-transparent via-primary/40 to-transparent opacity-0 transition-opacity duration-700 ${
              scrolled ? "opacity-100" : ""
            }`}
          />
          <div
            className={`absolute inset-x-0 bottom-0 h-px bg-linear-to-r from-transparent via-accent-blue/40 to-transparent opacity-0 transition-opacity duration-700 ${
              scrolled ? "opacity-100" : ""
            }`}
          />

          <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
            <Link
              href="/"
              onClick={(event) => {
                if (pathname !== "/") return;
                event.preventDefault();
                window.history.replaceState(null, "", "/");
                window.scrollTo({ top: 0, behavior: "smooth" });
                setActiveSection(null);
                setMobileOpen(false);
              }}
              className="flex items-center gap-2"
            >
              <motion.div
                whileHover={{ scale: 1.05, rotate: -3 }}
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-linear-to-br from-primary to-primary-dark text-xs font-bold text-background shadow-lg shadow-primary/20"
              >
                M
              </motion.div>
              <span className="text-lg font-semibold tracking-tight text-text">
                Mix<span className="text-primary">Mind</span>
              </span>
            </Link>

            <nav className="hidden items-center gap-1 md:flex">
              {NAV_LINKS.map((link) => {
                const active = isActive(link.sectionId);
                return (
                  <a
                    key={link.href}
                    href={link.href}
                    onClick={(event) => {
                      event.preventDefault();
                      navigateTo(link.sectionId);
                    }}
                    className={`relative flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm transition-colors duration-300 ${
                      active
                        ? "text-primary"
                        : "text-text-secondary hover:bg-card hover:text-text"
                    }`}
                  >
                    {active && (
                      <motion.span
                        layoutId="nav-active"
                        className="absolute inset-0 rounded-lg bg-primary/10"
                        transition={{ type: "spring", stiffness: 380, damping: 30 }}
                      />
                    )}
                    <link.icon className="relative h-4 w-4" />
                    <span className="relative">{link.label}</span>
                  </a>
                );
              })}
              <div className="ml-4">
                {loading ? (
                  <div className="h-9 w-20 animate-pulse rounded-lg bg-card" />
                ) : isAuthenticated ? (
                  <UserDropdown />
                ) : (
                  <Button
                    variant="premium"
                    size="sm"
                    onClick={() => setAuthOpen(true)}
                  >
                    Sign In
                  </Button>
                )}
              </div>
            </nav>

            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="flex h-9 w-9 items-center justify-center rounded-lg text-text-secondary hover:text-text md:hidden"
              aria-label={mobileOpen ? "Close menu" : "Open menu"}
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute inset-x-0 top-full mx-4 mt-1 overflow-hidden rounded-2xl border border-border/50 bg-background/95 backdrop-blur-2xl shadow-2xl"
            >
              <nav className="flex flex-col gap-1 p-3">
                {NAV_LINKS.map((link) => {
                  const active = isActive(link.sectionId);
                  return (
                    <a
                      key={link.href}
                      href={link.href}
                      onClick={(event) => {
                        event.preventDefault();
                        navigateTo(link.sectionId);
                      }}
                      className={`flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                        active
                          ? "bg-primary/10 text-primary"
                          : "text-text-secondary hover:text-text hover:bg-card"
                      }`}
                    >
                      <link.icon className="h-4 w-4" />
                      {link.label}
                    </a>
                  );
                })}
                <div className="mt-2 border-t border-border/50 pt-2">
                  {loading ? (
                    <div className="h-10 animate-pulse rounded-lg bg-card" />
                  ) : isAuthenticated ? (
                    <a
                      href="/dashboard"
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-2.5 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
                    >
                      <LayoutDashboard className="h-4 w-4" />
                      Dashboard
                    </a>
                  ) : (
                    <button
                      onClick={() => {
                        setMobileOpen(false);
                        setAuthOpen(true);
                      }}
                      className="w-full rounded-lg bg-primary px-3 py-2.5 text-sm font-medium text-background transition-colors hover:bg-primary-dark"
                    >
                      Sign In
                    </button>
                  )}
                </div>
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>

      <AuthDialog open={authOpen} onOpenChange={setAuthOpen} />
    </>
  );
}
