"use client";

import { motion } from "framer-motion";

const FOOTER_LINKS = {
  Product: [
    { label: "How It Works", href: "#how-it-works" },
    { label: "Features", href: "#features" },
    { label: "Demo", href: "#demo" },
    { label: "Technologies", href: "#technologies" },
  ],
  Technologies: [
    { label: "Python / FastAPI", href: "#technologies" },
    { label: "Machine Learning", href: "#technologies" },
    { label: "Next.js / React", href: "#technologies" },
    { label: "Docker", href: "#technologies" },
  ],
  Resources: [
    { label: "Documentation", href: "#" },
    { label: "GitHub", href: "#" },
    { label: "API Reference", href: "#" },
    { label: "Changelog", href: "#" },
  ],
  Legal: [
    { label: "License", href: "#" },
    { label: "Terms of Service", href: "#" },
    { label: "Privacy Policy", href: "#" },
    { label: "Contact", href: "#" },
  ],
};

export function Footer() {
  return (
    <footer className="border-t border-border/50 pt-16 pb-8">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <a href="#" className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary-dark text-xs font-bold text-background">
                M
              </div>
              <span className="text-lg font-semibold tracking-tight text-text">
                Mix<span className="text-primary">Mind</span>
              </span>
            </a>
            <p className="max-w-sm text-sm leading-relaxed text-text-secondary">
              AI-powered DJ track analysis platform. Upload, analyze, and get
              intelligent recommendations for seamless harmonic transitions.
            </p>
            <div className="mt-6 flex items-center gap-3">
              {["GitHub", "Twitter", "Discord"].map((platform) => (
                <motion.a
                  key={platform}
                  href="#"
                  whileHover={{ y: -2 }}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card text-xs font-medium text-text-secondary transition-all duration-300 hover:border-primary/20 hover:text-primary"
                >
                  {platform[0]}
                </motion.a>
              ))}
            </div>
          </div>

          {Object.entries(FOOTER_LINKS).map(([category, links]) => (
            <div key={category}>
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-text-tertiary">
                {category}
              </h3>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-text-secondary transition-colors duration-300 hover:text-primary"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 border-t border-border/50 pt-6">
          <div className="flex flex-col items-center justify-between gap-4 text-[14px] text-text-tertiary sm:flex-row">
            <p>
              &copy; {new Date().getFullYear()} MixMind AI. All rights reserved.
            </p>
            <p>
              Crafted by Daniel Thielmann for DJs who turn precision and
              technology into unforgettable sets.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
