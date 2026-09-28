"""Image preprocessing for plate OCR."""

from __future__ import annotations

import cv2
import numpy as np


def preprocess_plate_crop(crop: np.ndarray) -> np.ndarray:
    """Normalize the plate crop to improve OCR robustness."""
    if crop is None or crop.size == 0:
        return crop

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh
