"""Tracking and trajectory logic for ANPR platform."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TrackObservation:
    """Track observation container."""

    timestamp: datetime
    bbox: tuple[float, float, float, float]
    center: tuple[float, float]
    confidence: float
    class_name: str
    plate: str | None = None


@dataclass
class VehicleTrack:
    """Minimal vehicle track state."""

    track_id: int
    camera_id: str
    first_timestamp: datetime
    last_timestamp: datetime
    bbox: tuple[float, float, float, float]
    vehicle_class: str
    center_history: list[tuple[float, float]] = field(default_factory=list)
    observations: list[TrackObservation] = field(default_factory=list)
    consensus_plate: str | None = None
    detection_confidence: float = 0.0
    active: bool = True

    def update(self, timestamp: datetime, bbox: tuple[float, float, float, float], center: tuple[float, float], confidence: float, class_name: str, plate: str | None = None) -> None:
        self.last_timestamp = timestamp
        self.bbox = bbox
        self.detection_confidence = confidence
        self.vehicle_class = class_name
        self.center_history.append(center)
        if plate:
            self.consensus_plate = plate
        self.observations.append(
            TrackObservation(
                timestamp=timestamp,
                bbox=bbox,
                center=center,
                confidence=confidence,
                class_name=class_name,
                plate=plate,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "camera_id": self.camera_id,
            "first_timestamp": self.first_timestamp.isoformat(),
            "last_timestamp": self.last_timestamp.isoformat(),
            "bbox": list(self.bbox),
            "vehicle_class": self.vehicle_class,
            "center_history": [list(item) for item in self.center_history],
            "consensus_plate": self.consensus_plate,
            "detection_confidence": self.detection_confidence,
            "active": self.active,
        }


class VehicleTracker:
    """Simple centroid fallback tracker for local use when ByteTrack is unavailable."""

    def __init__(self, max_distance: float = 80.0) -> None:
        self.max_distance = max_distance
        self.tracks: dict[int, VehicleTrack] = {}
        self.next_track_id = 1

    def _iou(self, box_a: tuple[float, float, float, float], box_b: tuple[float, float, float, float]) -> float:
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])
        inter_w = max(0.0, x2 - x1)
        inter_h = max(0.0, y2 - y1)
        inter = inter_w * inter_h
        area_a = max(0.0, (box_a[2] - box_a[0]) * (box_a[3] - box_a[1]))
        area_b = max(0.0, (box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    def _centroid_distance(self, center_a: tuple[float, float], center_b: tuple[float, float]) -> float:
        return ((center_a[0] - center_b[0]) ** 2 + (center_a[1] - center_b[1]) ** 2) ** 0.5

    def update(self, detections: list[dict[str, Any]], camera_id: str, timestamp: datetime) -> list[VehicleTrack]:
        if not detections:
            return []

        for detection in detections:
            bbox = tuple(detection.get("bbox", (0, 0, 0, 0)))
            if len(bbox) != 4:
                continue
            center = tuple(detection.get("center", (0.0, 0.0)))
            class_name = str(detection.get("class_name", "unknown"))
            confidence = float(detection.get("confidence", 0.0))
            plate = detection.get("plate")

            matched_track_id = None
            matched_distance = None
            for track_id, track in self.tracks.items():
                if track.camera_id != camera_id:
                    continue
                last_center = track.center_history[-1] if track.center_history else track.bbox[:2]
                distance = self._centroid_distance(center, last_center)
                iou = self._iou(bbox, track.bbox)
                if distance <= self.max_distance or iou > 0.1:
                    if matched_distance is None or distance < matched_distance:
                        matched_track_id = track_id
                        matched_distance = distance

            if matched_track_id is not None:
                track = self.tracks[matched_track_id]
                track.update(timestamp, bbox, center, confidence, class_name, plate)
            else:
                track = VehicleTrack(
                    track_id=self.next_track_id,
                    camera_id=camera_id,
                    first_timestamp=timestamp,
                    last_timestamp=timestamp,
                    bbox=bbox,
                    vehicle_class=class_name,
                    center_history=[center],
                    detection_confidence=confidence,
                    active=True,
                )
                self.tracks[self.next_track_id] = track
                self.next_track_id += 1

        return list(self.tracks.values())
