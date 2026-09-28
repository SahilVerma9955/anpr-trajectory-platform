"""Unified detection wrapper that combines vehicle and plate detection."""

from __future__ import annotations

from typing import Any

import numpy as np

from .plate_detector import PlateDetector
from .vehicle_detector import DetectionResult, VehicleDetector


class UnifiedDetector:
    """High-level detector used by the pipeline to obtain vehicles and plate candidates."""

    def __init__(self, vehicle_detector: VehicleDetector | None = None, plate_detector: PlateDetector | None = None) -> None:
        self.vehicle_detector = vehicle_detector or VehicleDetector()
        self.plate_detector = plate_detector or PlateDetector()

    def detect_frame(self, image: np.ndarray) -> tuple[list[DetectionResult], list[dict[str, Any]]]:
        vehicles = self.vehicle_detector.detect_image(image)
        plate_candidates: list[dict[str, Any]] = []
        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle.bbox
            crop = image[int(y1): int(y2), int(x1): int(x2)]
            if crop.size == 0:
                continue
            plate_candidates.extend(
                {
                    "vehicle": vehicle,
                    **candidate,
                }
                for candidate in self.plate_detector.detect(crop)
            )
        return vehicles, plate_candidates

    def detect_image(self, image: np.ndarray) -> dict[str, Any]:
        vehicles, plate_candidates = self.detect_frame(image)
        return {
            "vehicles": [v.to_dict() for v in vehicles],
            "plate_candidates": plate_candidates,
            "active_plate_mode": "custom_model" if self.plate_detector.is_custom_model_available() else "baseline",
        }
