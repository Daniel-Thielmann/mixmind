import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/landing/Header";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MixMind AI — AI-Powered DJ Track Analysis",
  description:
    "Upload your tracks. Let MixMind analyze BPM, energy, harmonic keys, and compatibility. Get AI-powered recommendations for seamless DJ transitions.",
  openGraph: {
    title: "MixMind AI",
    description: "AI-Powered DJ Track Analysis Platform",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={geist.className}>
      <body className="flex min-h-screen flex-col bg-background text-text antialiased">
        <Header />
        <main className="flex flex-1 flex-col">{children}</main>
      </body>
    </html>
  );
}