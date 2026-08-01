import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { UploadForm } from "@/components/upload-form";

export default function AnalyzerPage() {
  return (
    <main className="min-h-screen bg-background px-6 py-10 md:py-16">
      <div className="mx-auto max-w-6xl">
        <Link href="/" className="mb-12 inline-flex items-center gap-2 text-sm text-text-secondary transition-colors hover:text-text">
          <ArrowLeft size={16} /> Back to MixMind
        </Link>
        <div className="mb-10 max-w-3xl">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
            <Sparkles size={13} /> MixMind Analyzer
          </div>
          <h1 className="text-4xl font-bold tracking-tight md:text-6xl">Find the transition before the crowd hears it.</h1>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-text-secondary">
            Upload two audio files or choose tracks directly from Spotify. MixMind handles acquisition, compatibility, risks, timing and your transition plan.
          </p>
        </div>
        <UploadForm />
      </div>
    </main>
  );
}
