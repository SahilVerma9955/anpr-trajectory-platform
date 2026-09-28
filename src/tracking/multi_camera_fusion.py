"""Multi-camera association helpers for vehicle route fusion."""

from __future__ import annotations

from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the Haversine distance in kilometers between two lat/lon points."""
    radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius * c


class MultiCameraFusion:
    """Basic route plausibility logic for associating tracks across cameras."""

    def __init__(self, camera_positions: dict[str, dict[str, float]] | None = None) -> None:
        self.camera_positions = camera_positions or {}

    def plausible_link(
        self,
        *,
        normalized_plate_similarity: float,
        ocr_confidence: float,
        time_gap_seconds: float,
        camera_a: str,
        camera_b: str,
        speed_kmh_estimate: float | None = None,
    ) -> bool:
        """Determine whether two sightings are plausibly the same vehicle."""
        if normalized_plate_similarity < 0.8 and ocr_confidence < 0.6:
            return False

        if time_gap_seconds < 0:
            return False

        if speed_kmh_estimate is not None and speed_kmh_estimate > 180:
            return False

        if camera_a in self.camera_positions and camera_b in self.camera_positions:
            pos_a = self.camera_positions[camera_a]
            pos_b = self.camera_positions[camera_b]
            distance_km = haversine_km(pos_a["latitude"], pos_a["longitude"], pos_b["latitude"], pos_b["longitude"])
            if time_gap_seconds > 0:
                implied_speed = (distance_km / (time_gap_seconds / 3600.0)) if time_gap_seconds > 0 else 0.0
                if implied_speed > 180:
                    return False

        return True
