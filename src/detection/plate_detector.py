"""Vehicle detection wrapper based on Ultralytics YOLO."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


@dataclass
class DetectionResult:
    """Single vehicle detection result."""

    class_name: str
    class_id: int
    confidence: float
    bbox: tuple[float, float, float, float]
    center: tuple[float, float]
    frame_width: int
    frame_height: int
    frame_index: int | None = None
    track_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "class_name": self.class_name,
            "class_id": self.class_id,
            "confidence": self.confidence,
            "bbox": list(self.bbox),
            "center": list(self.center),
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "frame_index": self.frame_index,
            "track_id": self.track_id,
        }


class VehicleDetector:
    """Use YOLO to detect vehicles and optionally track them with ByteTrack."""

    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        confidence: float = 0.35,
        iou: float = 0.50,
        image_size: int = 640,
        device: str = "auto",
        classes: list[str] | None = None,
    ) -> None:
        self.model_name = model_name
        self.confidence = confidence
        self.iou = iou
        self.image_size = image_size
        self.device = device
        self.classes = classes or ["car", "motorcycle", "bus", "truck", "auto-rickshaw"]
        self.model = YOLO(model_name)

    @staticmethod
    def _map_class_name(class_name: str | None) -> str:
        aliases = {
            "car": "car",
            "vehicle": "car",
            "motorcycle": "motorcycle",
            "bike": "motorcycle",
            "bus": "bus",
            "truck": "truck",
            "auto": "auto-rickshaw",
            "auto-rickshaw": "auto-rickshaw",
        }
        if class_name is None:
            return "unknown"
        return aliases.get(class_name.lower(), class_name.lower())

    def _class_filter(self, names: list[str]) -> set[int]:
        class_map = {
            "car": 2,
            "motorcycle": 3,
            "bus": 5,
            "truck": 7,
            "auto-rickshaw": 0,
        }
        allowed_ids = set()
        for value in names:
            normalized = self._map_class_name(value)
            if normalized in class_map:
                allowed_ids.add(class_map[normalized])
        return allowed_ids

    def detect_image(self, image: np.ndarray, *, frame_index: int | None = None) -> list[DetectionResult]:
        """Run inference for a single image and return typed detections."""
        outputs = self.model(
            image,
            conf=self.confidence,
            iou=self.iou,
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )

        results: list[DetectionResult] = []
        allowed_classes = self._class_filter(self.classes)
        prediction = outputs[0]
        if prediction is None or prediction.boxes is None:
            return results

        for box in prediction.boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            class_id = int(box.cls[0])
            if allowed_classes and class_id not in allowed_classes:
                continue

            class_name = self.model.names.get(class_id, "unknown")
            class_name = self._map_class_name(class_name)
            bbox = (x1, y1, x2, y2)
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            results.append(
                DetectionResult(
                    class_name=class_name,
                    class_id=class_id,
                    confidence=conf,
                    bbox=bbox,
                    center=(center_x, center_y),
                    frame_width=image.shape[1],
                    frame_height=image.shape[0],
                    frame_index=frame_index,
                )
            )
        return results

    def detect_video(self, video_path: str | Path, output_path: str | Path | None = None) -> list[DetectionResult]:
        """Run video inference and optionally save a labeled output video."""
        source = Path(video_path)
        cap = cv2.VideoCapture(str(source))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        writer = None
        output_target = Path(output_path) if output_path else None
        if output_target is not None:
            output_target.parent.mkdir(parents=True, exist_ok=True)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(output_target), fourcc, fps, (width, height))

        all_results: list[DetectionResult] = []
        frame_index = 0
        start = time.perf_counter()
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                detections = self.detect_image(frame, frame_index=frame_index)
                all_results.extend(detections)
                for det in detections:
                    x1, y1, x2, y2 = det.bbox
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    label = f"{det.class_name} {det.confidence:.2f}"
                    cv2.putText(frame, label, (int(x1), max(20, int(y1)-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                if writer is not None:
                    writer.write(frame)
                frame_index += 1
        finally:
            cap.release()
            if writer is not None:
                writer.release()

        elapsed = time.perf_counter() - start
        print(f"Vehicle detection finished in {elapsed:.2f}s; detections={len(all_results)}")
        return all_results
