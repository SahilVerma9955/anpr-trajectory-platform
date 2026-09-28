"""Database CRUD and schema operations."""

from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy.orm import Session

from .models import Alert, AnalyticsSnapshot, BlacklistEntry, Camera, Detection, OCRObservation, Trajectory, Vehicle, Video


class Crud:
    """Basic CRUD helpers for the stats and detection tables."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_camera(self, camera_id: str, latitude: float | None = None, longitude: float | None = None, orientation: int | None = None, road_segment: str | None = None) -> Camera:
        camera = Camera(camera_id=camera_id, latitude=latitude, longitude=longitude, orientation=orientation, road_segment=road_segment)
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        return camera

    def list_cameras(self) -> list[Camera]:
        return self.db.query(Camera).order_by(Camera.camera_id).all()

    def list_videos(self) -> list[Video]:
        return self.db.query(Video).order_by(Video.id.desc()).all()

    def create_video(self, video_id: str, camera_id: str | None = None, source_path: str | None = None, frame_count: int | None = None, fps: float | None = None, width: int | None = None, height: int | None = None, duration_seconds: float | None = None) -> Video:
        video = Video(video_id=video_id, camera_id=camera_id, source_path=source_path, frame_count=frame_count, fps=fps, width=width, height=height, duration_seconds=duration_seconds)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def create_detection(self, **kwargs: Any) -> Detection:
        detection = Detection(**kwargs)
        self.db.add(detection)
        self.db.commit()
        self.db.refresh(detection)
        return detection

    def create_ocr_observation(self, **kwargs: Any) -> OCRObservation:
        observation = OCRObservation(**kwargs)
        self.db.add(observation)
        self.db.commit()
        self.db.refresh(observation)
        return observation

    def create_alert(self, plate: str, normalized_plate: str, severity: str = "medium", message: str = "Alert") -> Alert:
        alert = Alert(plate=plate, normalized_plate=normalized_plate, severity=severity, message=message)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def list_alerts(self) -> list[Alert]:
        return self.db.query(Alert).order_by(Alert.created_at.desc()).all()

    def add_blacklist(self, plate: str, normalized_plate: str, reason: str = "manual") -> BlacklistEntry:
        entry = BlacklistEntry(plate=plate, normalized_plate=normalized_plate, reason=reason)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def remove_blacklist(self, plate: str) -> bool:
        entry = self.db.query(BlacklistEntry).filter(BlacklistEntry.normalized_plate == plate).first()
        if not entry:
            return False
        self.db.delete(entry)
        self.db.commit()
        return True

    def get_vehicle_by_plate(self, plate: str) -> Vehicle | None:
        return self.db.query(Vehicle).filter(Vehicle.normalized_plate == plate).first()
