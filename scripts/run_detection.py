#!/usr/bin/env python3
"""Extract sampled frames from all videos in a directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.video.frame_extractor import extract_frames

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


def iter_videos(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract sampled frames from traffic videos.")
    parser.add_argument("--input", type=str, required=True, help="Directory containing raw videos")
    parser.add_argument("--output", type=str, default="data/frames", help="Directory for extracted frames")
    parser.add_argument("--every-n-frames", type=int, default=10, help="Sample every N-th frame")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    videos = iter_videos(input_dir)
    if not videos:
        print(f"No video files found under {input_dir}")
        return

    print(f"Found {len(videos)} video(s). Extracting every {args.every_n_frames} frames to {output_dir}...")
    for video in videos:
        try:
            records = extract_frames(video, output_dir, every_n_frames=args.every_n_frames)
            print(f"- {video.name}: extracted {len(records)} frames")
        except Exception as exc:  # pragma: no cover - CLI resilience
            print(f"- {video.name}: failed to extract frames ({exc})")


if __name__ == "__main__":
    main()
