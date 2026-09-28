"""OCR reader wrapper for Indian license plates."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .plate_preprocessor import preprocess_plate_crop
from .plate_validator import validate_plate_text


class PlateReader:
    """A lightweight OCR wrapper that tries to read a plate-like text from a crop."""

    def __init__(self, engine: str = "easyocr") -> None:
        self.engine = engine.lower()
        self.reader = None
        if engine.lower() == "easyocr":
            try:
                import easyocr

                self.reader = easyocr.Reader(["en"], gpu=False)
            except Exception:  # pragma: no cover - optional dependency
                self.reader = None

    def _extract_text(self, image: np.ndarray) -> tuple[str, float]:
        processed = preprocess_plate_crop(image)
        if self.reader is None:
            return "", 0.0

        try:
            results = self.reader.readtext(processed)
        except Exception:  # pragma: no cover - OCR engine may fail
            return "", 0.0

        if not results:
            return "", 0.0

        text = ""
        confidence = 0.0
        for item in results:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                try:
                    value = str(item[1])
                except Exception:
                    continue
                if value:
                    text = text + value + " "
                    if len(item) >= 3 and isinstance(item[2], (int, float)):
                        confidence = max(confidence, float(item[2]))
        return text.strip(), confidence

    def read(self, image: np.ndarray) -> dict[str, Any]:
        """Run OCR on a plate crop and validate the result."""
        raw_text, confidence = self._extract_text(image)
        normalized = re.sub(r"[^A-Z0-9]", "", raw_text.upper())

        validation = validate_plate_text(normalized)
        return {
            "raw_text": raw_text,
            "normalized_text": normalized,
            "confidence": confidence,
            "validation_status": validation.is_valid,
            "reason": validation.reason,
            "raw_validation": validation.to_dict(),
        }
