import { UploadForm } from "@/components/upload-form";

export default function Home() {
  return (
    <>
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight md:text-6xl">MixMind</h1>
        <p className="mt-4 text-text-secondary md:text-lg">
          AI Powered DJ Track Analysis Platform
        </p>
      </div>
      <UploadForm />
    </>
  );
}
