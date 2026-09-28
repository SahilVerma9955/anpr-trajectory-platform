"""Video metadata utilities for ANPR processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2


@dataclass
class VideoMetadata:
    """Basic metadata derived from a video file."""

    filename: str
    path: str
    frame_count: int = 0
    fps: float = 0.0
    width: int = 0
    height: int = 0
    duration_seconds: float = 0.0
    status: str = "unknown"
    error: str | None = None
    camera_id: str | None = None
    video_id: str | None = None
    frame_count_estimate: int | None = None

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "path": self.path,
            "frame_count": self.frame_count,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "error": self.error,
            "camera_id": self.camera_id,
            "video_id": self.video_id,
        }


def extract_video_metadata(video_path: str | Path) -> VideoMetadata:
    """Open a video and extract metadata using OpenCV."""
    path = Path(video_path)
    metadata = VideoMetadata(filename=path.name, path=str(path))
    if not path.exists():
        metadata.status = "missing"
        metadata.error = f"File not found: {path}"
        return metadata

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        metadata.status = "unreadable"
        metadata.error = "OpenCV could not open the video file."
        return metadata

    try:
        metadata.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        metadata.fps = float(cap.get(cv2.CAP_PROP_FPS))
        metadata.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        metadata.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if metadata.fps > 0:
            metadata.duration_seconds = metadata.frame_count / metadata.fps
        metadata.status = "ok"
    except Exception as exc:  # pragma: no cover - runtime safety
        metadata.status = "error"
        metadata.error = str(exc)
    finally:
        cap.release()

    return metadata
