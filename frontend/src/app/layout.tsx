import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MixMind AI",
  description: "AI Powered DJ Track Analysis Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={geist.className}>
      <body className="flex min-h-screen flex-col bg-background text-text antialiased">
        <header className="flex h-14 items-center justify-center border-b border-zinc-800">
          <span className="text-lg font-bold text-primary">MixMind</span>
        </header>
        <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col items-center justify-center px-4 py-16">
          {children}
        </main>
        <footer className="flex h-14 items-center justify-center border-t border-zinc-800">
          <span className="text-sm text-zinc-600">&copy; {new Date().getFullYear()} MixMind AI</span>
        </footer>
      </body>
    </html>
  );
}
