"""Plate detection module with a baseline inference-only fallback mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


class PlateDetector:
    """A minimal plate detector that searches for plate-like regions in a vehicle crop."""

    def __init__(self, model_path: str | Path | None = None, confidence: float = 0.25) -> None:
        self.model_path = Path(model_path) if model_path else None
        self.confidence = confidence
        self.active_model = self.model_path.exists() if self.model_path else None

    def is_custom_model_available(self) -> bool:
        return bool(self.model_path and self.model_path.exists())

    def detect(self, vehicle_crop: np.ndarray) -> list[dict[str, Any]]:
        """Use a fallback heuristic to find a likely plate region inside a vehicle ROI."""
        if vehicle_crop is None or vehicle_crop.size == 0:
            return []

        height, width = vehicle_crop.shape[:2]
        if height < 20 or width < 20:
            return []

        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
        if gray.size == 0:
            return []

        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates: list[dict[str, Any]] = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < 0.1 * width or h < 0.05 * height:
                continue
            if w > 0.9 * width or h > 0.8 * height:
                continue
            score = (w * h) / (width * height)
            if score < 0.01:
                continue
            candidates.append(
                {
                    "bbox": (x, y, x + w, y + h),
                    "confidence": min(0.95, max(0.25, score * 10.0)),
                    "class_name": "plate_candidate",
                    "class_id": 0,
                }
            )

        candidates.sort(key=lambda item: item["confidence"], reverse=True)
        return candidates[:3]
