#!/usr/bin/env python3
"""Inspect the downloaded dataset, report file types, and summarize dataset suitability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_PATH = PROCESSED_DIR / "dataset_report.json"

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
ANNOTATION_EXTENSIONS = {".txt", ".csv", ".json", ".xml", ".yaml", ".yml"}


def list_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.rglob("*") if p.is_file())


def detect_files(file_list: list[Path]) -> dict[str, list[str]]:
    videos: list[str] = []
    images: list[str] = []
    annotations: list[str] = []

    for path in file_list:
        suffix = path.suffix.lower()
        if suffix in VIDEO_EXTENSIONS:
            videos.append(str(path.relative_to(ROOT)))
        elif suffix in IMAGE_EXTENSIONS:
            images.append(str(path.relative_to(ROOT)))
        elif suffix in ANNOTATION_EXTENSIONS:
            annotations.append(str(path.relative_to(ROOT)))

    return {"videos": videos, "images": images, "annotations": annotations}


def read_video_metadata(video_path: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "filename": str(video_path.relative_to(ROOT)),
        "exists": video_path.exists(),
        "frame_count": 0,
        "fps": 0.0,
        "width": 0,
        "height": 0,
        "duration_seconds": 0.0,
        "status": "error",
    }

    if not video_path.exists():
        return metadata

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        metadata["status"] = "unreadable"
        return metadata

    try:
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0.0

        metadata.update(
            {
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height,
                "duration_seconds": duration,
                "status": "ok",
            }
        )
    finally:
        capture.release()

    return metadata


def summarize_dataset_support(annotations: list[str]) -> dict[str, bool | str]:
    has_yolo_txt = any(path.lower().endswith(".txt") for path in annotations)
    has_csv_json = any(path.lower().endswith((".csv", ".json")) for path in annotations)
    has_xml = any(path.lower().endswith(".xml") for path in annotations)
    has_yaml = any(path.lower().endswith((".yaml", ".yml")) for path in annotations)

    return {
        "vehicle_detection_training": bool(has_yolo_txt or has_csv_json or has_xml or has_yaml),
        "vehicle_tracking": True,
        "license_plate_detection_training": bool(has_yolo_txt or has_csv_json or has_xml or has_yaml),
        "ocr_training": bool(has_csv_json or has_yaml),
        "traffic_analytics": True,
        "annotation_status": "annotations_present" if annotations else "no_annotations_detected",
        "notes": "The dataset may support training only if annotation files are valid and correspond to the actual video frames. Plate detection training requires plate bounding boxes; this script does not assume such labels exist.",
        "plate_training_possible": bool(has_yolo_txt or has_csv_json or has_xml),
    }


def generate_report() -> dict[str, Any]:
    file_list = list_files(RAW_DIR)
    detected = detect_files(file_list)

    video_metadata = []
    for video in detected["videos"]:
        video_path = ROOT / video
        video_metadata.append(read_video_metadata(video_path))

    support_summary = summarize_dataset_support(detected["annotations"])

    report = {
        "dataset_root": str(RAW_DIR.relative_to(ROOT)),
        "files_found": len(file_list),
        "video_count": len(detected["videos"]),
        "image_count": len(detected["images"]),
        "annotation_count": len(detected["annotations"]),
        "videos": detected["videos"],
        "images": detected["images"],
        "annotations": detected["annotations"],
        "video_metadata": video_metadata,
        "dataset_support": support_summary,
        "notes": [
            "The dataset may contain traffic videos without plate annotations.",
            "Any custom plate detection training should only proceed after confirming real annotation files and image-label alignment.",
            "Without plate annotations, the platform should fall back to pretrained vehicle detection and OCR as a baseline.",
        ],
    }
    return report


def print_report(report: dict[str, Any]) -> None:
    print("=" * 80)
    print("Indian Traffic Dataset Inspection Report")
    print("=" * 80)
    print(f"Dataset root: {report['dataset_root']}")
    print(f"Files found: {report['files_found']}")
    print(f"Videos: {report['video_count']}")
    print(f"Images: {report['image_count']}")
    print(f"Annotations: {report['annotation_count']}")
    print()

    if report["videos"]:
        print("Video metadata:")
        for item in report["video_metadata"]:
            print(f"- {item['filename']}: fps={item['fps']}, frames={item['frame_count']}, size={item['width']}x{item['height']}, duration={item['duration_seconds']:.2f}s, status={item['status']}")
    else:
        print("No videos detected in data/raw.")

    if report["annotations"]:
        print("Detected annotation files:")
        for item in report["annotations"]:
            print(f"- {item}")
    else:
        print("No annotation files detected; dataset is inference-only unless labels are added later.")

    print()
    support = report["dataset_support"]
    print("Dataset capability summary:")
    for key, value in support.items():
        if key in {"vehicle_detection_training", "vehicle_tracking", "license_plate_detection_training", "ocr_training", "traffic_analytics", "plate_training_possible"}:
            print(f"- {key}: {value}")
    print(f"- annotation_status: {support['annotation_status']}")
    print(f"- notes: {support['notes']}")
    print("=" * 80)


if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    report = generate_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print_report(report)
    print(f"Dataset report written to: {REPORT_PATH}")
    if not report["videos"]:
        print("No videos were found. The project should still be runnable with a future dataset or sample inputs.")
