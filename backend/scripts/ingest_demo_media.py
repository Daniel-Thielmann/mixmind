"""Offline, idempotent ingestion for authorized MixMind demo media.

This command deliberately accepts local files only. It is not a downloader and
must never run from an HTTP request or application startup.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.application.dto.demo_media import DemoMediaManifest
from app.core.config import settings

PIPELINE_VERSION = "1.0.0"
MANIFEST_PATH = "demo/manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True)


def duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    value = float(result.stdout.strip())
    if value <= 0:
        raise RuntimeError(f"Invalid duration for {path.name}")
    return value


def local_file(value: str) -> Path:
    if value.startswith(("http://", "https://")):
        raise argparse.ArgumentTypeError("Only owner-provided local files are accepted")
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Media file does not exist: {path}")
    return path


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("--track-a", required=True, type=local_file)
    command.add_argument("--track-b", required=True, type=local_file)
    command.add_argument("--transition-source", required=True, type=local_file)
    command.add_argument("--video-source", required=True, type=local_file)
    command.add_argument("--track-a-title", required=True)
    command.add_argument("--track-b-title", required=True)
    command.add_argument("--preview-seconds", type=float, default=45.0)
    command.add_argument("--transition-start", type=float, default=4620.0)
    command.add_argument("--video-start", type=float, default=18600.0)
    command.add_argument("--force", action="store_true")
    command.add_argument(
        "--confirm-authorized",
        action="store_true",
        help="Confirm that the supplied local media is licensed for this use.",
    )
    return command


def encode_audio(source: Path, output: Path, start: float, length: float) -> None:
    run([
        "ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-i", str(source),
        "-t", str(length), "-vn", "-ar", "44100", "-ac", "2", "-c:a", "aac",
        "-b:a", "192k", "-movflags", "+faststart", str(output),
    ])


def encode_video(source: Path, output: Path, start: float) -> None:
    run([
        "ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-i", str(source),
        "-t", "164", "-vf", "scale=-2:min(1080\\,ih)", "-c:v", "libx264",
        "-preset", "medium", "-crf", "26", "-maxrate", "2400k", "-bufsize", "4800k",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(output),
    ])


def make_poster(video: Path, output: Path) -> None:
    run([
        "ffmpeg", "-nostdin", "-v", "error", "-ss", "1", "-i", str(video),
        "-frames:v", "1", "-vf", "scale=1280:-2", "-quality", "80", str(output),
    ])


def asset(
    path: Path,
    *,
    title: str,
    object_path: str,
    media_duration: float | None,
    original_start: float | None,
) -> dict[str, Any]:
    mime = mimetypes.guess_type(path.name)[0]
    if not mime:
        raise RuntimeError(f"Unable to determine MIME type for {path.name}")
    result: dict[str, Any] = {
        "title": title,
        "objectPath": object_path,
        "mimeType": mime,
        "sizeBytes": path.stat().st_size,
        "checksum": sha256(path),
        "processedAt": datetime.now(UTC).isoformat(),
        "pipelineVersion": PIPELINE_VERSION,
    }
    if media_duration is not None:
        result["duration"] = media_duration
    if original_start is not None and media_duration is not None:
        result["originalStart"] = original_start
        result["originalEnd"] = original_start + media_duration
    return result


def existing_manifest(storage: Any) -> dict[str, Any] | None:
    try:
        return json.loads(storage.download(MANIFEST_PATH).decode("utf-8"))
    except Exception:
        return None


def upload_verified(storage: Any, local: Path, metadata: dict[str, Any], force: bool) -> None:
    object_path = metadata["objectPath"]
    try:
        remote = storage.download(object_path)
    except Exception:
        remote = None
    if remote is not None and f"sha256:{hashlib.sha256(remote).hexdigest()}" == metadata["checksum"]:
        return
    if remote is not None and not force:
        raise RuntimeError(f"Remote object differs: {object_path}; use --force explicitly")
    options = {
        "content-type": metadata["mimeType"],
        "cache-control": "3600",
        "upsert": "true" if force else "false",
    }
    storage.upload(path=object_path, file=local.read_bytes(), file_options=options)
    uploaded = storage.download(object_path)
    if f"sha256:{hashlib.sha256(uploaded).hexdigest()}" != metadata["checksum"]:
        raise RuntimeError(f"Checksum validation failed after upload: {object_path}")


def main() -> int:
    args = parser().parse_args()
    if not args.confirm_authorized:
        raise SystemExit("Refusing ingestion without --confirm-authorized")
    if not settings.SUPABASE_URL or not settings.SUPABASE_SECRET_KEY:
        raise SystemExit("Supabase backend credentials are not configured")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("FFmpeg and FFprobe are required for offline ingestion")

    from supabase import create_client

    storage = create_client(
        settings.SUPABASE_URL, settings.SUPABASE_SECRET_KEY
    ).storage.from_(settings.SUPABASE_STORAGE_BUCKET)
    source_hashes = {
        name: sha256(path)
        for name, path in {
            "trackA": args.track_a,
            "trackB": args.track_b,
            "transition": args.transition_source,
            "video": args.video_source,
        }.items()
    }
    current = existing_manifest(storage)
    if current and current.get("sourceChecksums") == source_hashes and not args.force:
        print("Authorized demo media is already current; nothing to ingest.")
        return 0

    with tempfile.TemporaryDirectory(prefix="mixmind-demo-") as temporary:
        root = Path(temporary)
        files = {
            "trackA": root / "track-a-preview.m4a",
            "trackB": root / "track-b-preview.m4a",
            "transition": root / "transition.m4a",
            "video": root / "clip-1080p.mp4",
            "poster": root / "poster.webp",
        }
        encode_audio(args.track_a, files["trackA"], 0, args.preview_seconds)
        encode_audio(args.track_b, files["trackB"], 0, args.preview_seconds)
        encode_audio(args.transition_source, files["transition"], args.transition_start, 120)
        encode_video(args.video_source, files["video"], args.video_start)
        make_poster(files["video"], files["poster"])

        durations = {name: duration(path) for name, path in files.items() if name != "poster"}
        if abs(durations["transition"] - 120) > 1 or abs(durations["video"] - 164) > 1:
            raise RuntimeError("Encoded transition/video duration is outside tolerance")

        paths = {
            "trackA": "demo/claptone-transition/track-a-preview.m4a",
            "trackB": "demo/claptone-transition/track-b-preview.m4a",
            "transition": "demo/claptone-transition/transition.m4a",
            "video": "demo/dawn-patrol/clip-1080p.mp4",
            "poster": "demo/dawn-patrol/poster.webp",
        }
        titles = {
            "trackA": args.track_a_title,
            "trackB": args.track_b_title,
            "transition": "Claptone transition excerpt",
            "video": "Dawn Patrol: Antdot B2B Maz @ Warung Beach Club [6h Long Set]",
            "poster": "Dawn Patrol demonstration poster",
        }
        starts = {"trackA": 0.0, "trackB": 0.0, "transition": args.transition_start, "video": args.video_start, "poster": None}
        assets = {
            name: asset(
                file,
                title=titles[name],
                object_path=paths[name],
                media_duration=durations.get(name),
                original_start=starts[name],
            )
            for name, file in files.items()
        }
        manifest = {
            "id": "mixmind-demo-v1",
            "title": "MixMind real media demonstration",
            "relationship": "trackA + trackB -> transition; video is a separate analyzed set excerpt",
            "sourceChecksums": source_hashes,
            "assets": assets,
        }
        DemoMediaManifest.model_validate(manifest)
        for name, file in files.items():
            upload_verified(storage, file, assets[name], args.force)

        manifest_bytes = json.dumps(manifest, indent=2).encode()
        manifest_file = root / "manifest.json"
        manifest_file.write_bytes(manifest_bytes)
        manifest_meta = {
            "objectPath": MANIFEST_PATH,
            "mimeType": "application/json",
            "checksum": sha256(manifest_file),
        }
        upload_verified(storage, manifest_file, manifest_meta, args.force)
        total = sum(file.stat().st_size for file in files.values()) + len(manifest_bytes)
        print(f"Ingestion validated: {len(files)} media objects + manifest, {total} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
