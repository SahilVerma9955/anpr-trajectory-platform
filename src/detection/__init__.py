"""Frame extraction utilities for video processing."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2

from .metadata import VideoMetadata, extract_video_metadata


@dataclass
class FrameRecord:
    """Represents one extracted video frame and its metadata."""

    video_path: str
    frame_index: int
    timestamp_seconds: float
    output_path: str
    camera_id: str | None = None
    video_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "video_path": self.video_path,
            "frame_index": self.frame_index,
            "timestamp_seconds": self.timestamp_seconds,
            "output_path": self.output_path,
            "camera_id": self.camera_id,
            "video_id": self.video_id,
        }


def extract_frames(
    input_path: str | Path,
    output_dir: str | Path,
    every_n_frames: int = 10,
    *,
    camera_id: str | None = None,
    video_id: str | None = None,
) -> list[FrameRecord]:
    """Extract every N-th frame from a video and save them to disk."""
    source = Path(input_path)
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    metadata = extract_video_metadata(source)
    if metadata.status != "ok":
        raise ValueError(f"Cannot extract frames from unreadable video: {source} ({metadata.error})")

    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {source}")

    extracted: list[FrameRecord] = []
    frame_index = 0
    saved_index = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if frame_index % every_n_frames == 0:
                timestamp_seconds = frame_index / metadata.fps if metadata.fps > 0 else 0.0
                output_file = target_dir / f"{source.stem}_frame_{saved_index:06d}.jpg"
                success = cv2.imwrite(str(output_file), frame)
                if not success:
                    raise IOError(f"Failed writing frame {frame_index} to {output_file}")

                extracted.append(
                    FrameRecord(
                        video_path=str(source),
                        frame_index=frame_index,
                        timestamp_seconds=timestamp_seconds,
                        output_path=str(output_file),
                        camera_id=camera_id,
                        video_id=video_id,
                    )
                )
                saved_index += 1

            frame_index += 1
    finally:
        cap.release()

    metadata_path = target_dir / f"{source.stem}_frame_metadata.jsonl"
    with metadata_path.open("w", encoding="utf-8") as handle:
        for record in extracted:
            handle.write(json.dumps(record.to_dict()) + "\n")

    return extracted
