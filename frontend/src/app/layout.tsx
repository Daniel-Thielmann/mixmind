import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/header/Header";
import { AuthProvider } from "@/providers/AuthProvider";
import { ToastProvider } from "@/components/ui/toast";

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
    <html lang="en" data-scroll-behavior="smooth">
      <body className="flex min-h-screen flex-col bg-background text-text antialiased">
        <AuthProvider>
          <ToastProvider>
            <Header />
            <main className="flex flex-1 flex-col">{children}</main>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
