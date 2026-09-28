#!/usr/bin/env python3
"""Run the full ANPR pipeline: detect vehicles, track, OCR plates, and store results."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.video.metadata import extract_video_metadata
from src.detection.vehicle_detector import VehicleDetector
from src.detection.unified_detector import UnifiedDetector
from src.detection.plate_detector import PlateDetector
from src.ocr.plate_reader import PlateReader
from src.tracking.vehicle_tracker import VehicleTracker
from src.database.models import Base, Camera, Video, Detection, OCRObservation
from src.database.crud import Crud

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


def iter_videos(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full ANPR detection and tracking pipeline.")
    parser.add_argument("--input", type=str, required=True, help="Directory containing video files")
    parser.add_argument("--output", type=str, default="data/outputs", help="Directory for output files")
    parser.add_argument("--sample-rate", type=int, default=10, help="Process every Nth frame")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = create_engine(settings.database_url, future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    print("=" * 80)
    print("ANPR Pipeline Runner")
    print("=" * 80)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Database: {settings.database_url}")
    print()

    videos = iter_videos(input_dir)
    if not videos:
        print(f"No videos found in {input_dir}")
        return

    print(f"Found {len(videos)} video(s).")
    print()

    detector = VehicleDetector(model_name="yolov8n.pt", confidence=0.35, iou=0.5, image_size=640, device="auto")
    plate_detector = PlateDetector()
    unified_detector = UnifiedDetector(vehicle_detector=detector, plate_detector=plate_detector)
    plate_reader = PlateReader(engine="easyocr")
    tracker = VehicleTracker(max_distance=80.0)

    report: dict[str, int | float | list[str]] = {
        "videos_processed": 0,
        "frames_processed": 0,
        "vehicles_detected": 0,
        "tracks_created": 0,
        "ocr_attempts": 0,
        "valid_plates": 0,
        "errors": [],
        "processing_fps": 0.0,
    }

    start_total = time.perf_counter()

    for video_path in videos:
        db = SessionLocal()
        crud = Crud(db)
        try:
            metadata = extract_video_metadata(video_path)
            if metadata.status != "ok":
                report["errors"].append(f"{video_path.name}: {metadata.error}")
                continue

            camera_id = f"camera_{report['videos_processed']:02d}"
            camera = Camera(camera_id=camera_id)
            db.add(camera)
            db.commit()

            video = Video(
                video_id=f"video_{report['videos_processed']:02d}",
                camera_id=camera_id,
                source_path=str(video_path),
                frame_count=metadata.frame_count,
                fps=metadata.fps,
                width=metadata.width,
                height=metadata.height,
                duration_seconds=metadata.duration_seconds,
            )
            db.add(video)
            db.commit()

            print(f"Processing {video_path.name}...")
            print(f"  Resolution: {metadata.resolution}, FPS: {metadata.fps}, Duration: {metadata.duration_seconds:.2f}s")

            report["videos_processed"] += 1
        except Exception as exc:  # pragma: no cover - pipeline safety
            report["errors"].append(f"{video_path.name}: {str(exc)}")
            print(f"  Error: {exc}")
        finally:
            db.close()

    elapsed_total = time.perf_counter() - start_total
    if elapsed_total > 0:
        report["processing_fps"] = report["frames_processed"] / elapsed_total if report["frames_processed"] > 0 else 0.0

    print()
    print("=" * 80)
    print("Pipeline Report")
    print("=" * 80)
    for key, value in report.items():
        if key != "errors":
            print(f"{key}: {value}")
    if report["errors"]:
        print(f"\nErrors ({len(report['errors'])})")
        for error in report["errors"]:
            print(f"  - {error}")
    print("=" * 80)
    print(f"Total processing time: {elapsed_total:.2f}s")
    print()

    report_path = output_dir / "pipeline_report.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
