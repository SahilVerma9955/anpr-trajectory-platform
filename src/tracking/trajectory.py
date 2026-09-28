"""Trajectory helper for route-like state reconstruction."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TrajectoryPoint:
    """Single route point with a timestamp and coordinates."""

    timestamp: datetime
    x: float
    y: float
    camera_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "x": self.x,
            "y": self.y,
            "camera_id": self.camera_id,
        }


@dataclass
class Trajectory:
    """Preserve temporal order and allow approximate movement calculations."""

    plate: str | None = None
    camera_sequence: list[str] = field(default_factory=list)
    points: list[TrajectoryPoint] = field(default_factory=list)
    route_distance: float = 0.0
    duration_seconds: float = 0.0

    def append(self, timestamp: datetime, x: float, y: float, camera_id: str | None = None) -> None:
        self.points.append(TrajectoryPoint(timestamp=timestamp, x=x, y=y, camera_id=camera_id))
        if camera_id is not None and camera_id not in self.camera_sequence:
            self.camera_sequence.append(camera_id)

    def sort(self) -> None:
        self.points = sorted(self.points, key=lambda point: point.timestamp)

    def approximate_distance(self) -> float:
        total = 0.0
        for current, nxt in zip(self.points, self.points[1:]):
            total += ((nxt.x - current.x) ** 2 + (nxt.y - current.y) ** 2) ** 0.5
        self.route_distance = total
        return total

    def to_geojson_like(self) -> dict[str, Any]:
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"plate": self.plate, "camera_sequence": self.camera_sequence},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[point.x, point.y] for point in self.points],
                    },
                }
            ],
        }


class TrajectoryBuilder:
    """Create a trajectory from CCTV observations."""

    def __init__(self) -> None:
        self.trajectories: dict[str, Trajectory] = {}

    def add_point(self, plate: str, timestamp: datetime, x: float, y: float, camera_id: str | None = None) -> Trajectory:
        trajectory = self.trajectories.setdefault(plate, Trajectory(plate=plate))
        trajectory.append(timestamp, x, y, camera_id)
        trajectory.sort()
        if len(trajectory.points) > 1:
            trajectory.duration_seconds = (trajectory.points[-1].timestamp - trajectory.points[0].timestamp).total_seconds()
            trajectory.route_distance = trajectory.approximate_distance()
        return trajectory
