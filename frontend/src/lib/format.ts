export function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.round(totalSeconds % 60)
    .toString()
    .padStart(2, "0");

  return `${minutes}:${seconds}`;
}

export function formatEnergy(value: number): string {
  return value.toFixed(3);
}

export function resolveMediaUrl(imagePath: string): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured.");
  }

  if (/^https?:\/\//.test(imagePath)) {
    return imagePath;
  }

  return `${apiUrl.replace(/\/$/, "")}/${imagePath.replace(/^\//, "")}`;
}
