"use client";

interface UploadCardProps {
  label: string;
  fileName?: string;
  onFile: (file: File) => void;
}

export function UploadCard({ label, fileName, onFile }: UploadCardProps) {
  function handleClick() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "audio/*";
    input.onchange = () => {
      const file = input.files?.[0];
      if (file) {
        onFile(file);
      }
    };
    input.click();
  }

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file) {
      onFile(file);
    }
  }

  return (
    <article className="rounded-2xl border border-zinc-800 bg-card/80 p-6 shadow-[0_16px_50px_-30px_rgba(0,0,0,0.9)] backdrop-blur md:p-7">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-[0.15em] text-text-secondary">
        {label}
      </h3>
      <div
        onClick={handleClick}
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
        className="cursor-pointer rounded-xl border border-dashed border-zinc-700 bg-zinc-900/70 px-4 py-10 text-center transition hover:border-primary/70"
      >
        {fileName ? (
          <p className="truncate text-sm text-text">{fileName}</p>
        ) : (
          <>
            <p className="text-lg font-semibold text-text">Drop audio file</p>
            <p className="mt-1 text-xs text-text-secondary">or click to browse</p>
          </>
        )}
      </div>
    </article>
  );
}
