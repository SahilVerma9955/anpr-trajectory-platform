"""Analytics module for traffic metrics computation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


class TrafficDensity:
    """Compute vehicle density per region."""

    @staticmethod
    def calculate(detections: list[dict[str, Any]], time_window_seconds: int = 60) -> dict[str, Any]:
        """Count unique vehicles in a time window."""
        if not detections:
            return {"vehicle_count": 0, "density": 0.0, "confidence": "no_data"}
        unique_plates = set(d.get("normalized_plate") for d in detections if d.get("normalized_plate"))
        return {
            "vehicle_count": len(unique_plates),
            "density": len(unique_plates) / max(1, time_window_seconds),
            "confidence": "medium" if len(unique_plates) > 0 else "low",
        }


class TrafficFlow:
    """Compute flow rate (vehicles per minute)."""

    @staticmethod
    def calculate(detections: list[dict[str, Any]], time_window_seconds: int = 60) -> dict[str, Any]:
        """Vehicles per minute in a time window."""
        if not detections or time_window_seconds == 0:
            return {"vehicles_per_minute": 0.0, "confidence": "no_data"}
        unique_count = len(set(d.get("normalized_plate") for d in detections if d.get("normalized_plate")))
        minutes = time_window_seconds / 60.0
        return {"vehicles_per_minute": unique_count / max(1, minutes), "confidence": "medium" if unique_count > 0 else "low"}


class SpeedCalculator:
    """Estimate vehicle speed from trajectory or calibrated distance."""

    @staticmethod
    def calculate_from_trajectory(distance_meters: float, duration_seconds: float) -> float:
        """Calculate speed in km/h from distance and time."""
        if duration_seconds <= 0:
            return 0.0
        speed_ms = distance_meters / duration_seconds
        return speed_ms * 3.6

    @staticmethod
    def calculate_pixel_movement(detections: list[dict[str, Any]], fps: float = 30.0) -> float:
        """Estimate raw pixel displacement per second; requires calibration for real km/h."""
        if len(detections) < 2 or fps <= 0:
            return 0.0
        total_displacement = 0.0
        for current, nxt in zip(detections, detections[1:]):
            cx1 = current.get("center", (0, 0))[0]
            cy1 = current.get("center", (0, 0))[1]
            cx2 = nxt.get("center", (0, 0))[0]
            cy2 = nxt.get("center", (0, 0))[1]
            total_displacement += ((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2) ** 0.5
        return total_displacement / (len(detections) - 1) * fps


class CongestionCalculator:
    """Compute congestion index from speed data."""

    FREE_FLOW_SPEED_KMH = 50.0

    @classmethod
    def calculate(cls, average_speed_kmh: float, free_flow_speed_kmh: float | None = None) -> dict[str, Any]:
        """Return congestion index from 0 to 1."""
        ffs = free_flow_speed_kmh or cls.FREE_FLOW_SPEED_KMH
        if ffs <= 0:
            ffs = cls.FREE_FLOW_SPEED_KMH
        ratio = average_speed_kmh / ffs
        congestion_index = max(0.0, min(1.0, 1.0 - ratio))
        status = "free_flow" if congestion_index < 0.3 else "moderate" if congestion_index < 0.7 else "congested"
        return {
            "current_speed_kmh": average_speed_kmh,
            "free_flow_speed_kmh": ffs,
            "congestion_index": congestion_index,
            "status": status,
        }


class TrafficHeatmap:
    """Generate grid-based intensity data."""

    @staticmethod
    def generate(detections: list[dict[str, Any]], grid_size: int = 10, image_width: int = 1920, image_height: int = 1080) -> list[dict[str, Any]]:
        """Divide image into a grid and count detections per cell."""
        if not detections or grid_size <= 0:
            return []
        cell_width = image_width / grid_size
        cell_height = image_height / grid_size
        grid: dict[tuple[int, int], int] = {}
        for detection in detections:
            cx = detection.get("center", (0, 0))[0]
            cy = detection.get("center", (0, 0))[1]
            cell_x = int(cx / cell_width) if cell_width > 0 else 0
            cell_y = int(cy / cell_height) if cell_height > 0 else 0
            cell_x = min(cell_x, grid_size - 1)
            cell_y = min(cell_y, grid_size - 1)
            key = (cell_x, cell_y)
            grid[key] = grid.get(key, 0) + 1
        heatmap = []
        for (cell_x, cell_y), count in grid.items():
            heatmap.append(
                {
                    "grid_x": cell_x,
                    "grid_y": cell_y,
                    "x": cell_x * cell_width + cell_width / 2.0,
                    "y": cell_y * cell_height + cell_height / 2.0,
                    "intensity": count,
                }
            )
        return sorted(heatmap, key=lambda item: item["intensity"], reverse=True)


class ODMatrix:
    """Origin-destination matrix from trajectories."""

    @staticmethod
    def compute(trajectories: list[dict[str, Any]]) -> dict[str, int]:
        """Count vehicle transitions from origin to destination camera."""
        matrix: dict[str, int] = {}
        for trajectory in trajectories:
            cameras = trajectory.get("camera_sequence", [])
            if len(cameras) >= 2:
                origin = cameras[0]
                destination = cameras[-1]
                key = f"{origin}→{destination}"
                matrix[key] = matrix.get(key, 0) + 1
        return matrix
