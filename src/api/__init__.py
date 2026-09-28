"""Pydantic schemas for database and API objects."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=200)


class VideoSchema(BaseModel):
    id: int | None = None
    video_id: str | None = None
    camera_id: str | None = None
    source_path: str | None = None
    frame_count: int | None = None
    fps: float | None = None
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None


class VehicleSchema(BaseModel):
    id: int | None = None
    track_id: str | None = None
    camera_id: str | None = None
    plate: str | None = None
    normalized_plate: str | None = None
    vehicle_class: str | None = None
    confidence: float | None = None
    metadata_json: dict[str, Any] | None = None


class AlertSchema(BaseModel):
    id: int | None = None
    plate: str | None = None
    normalized_plate: str | None = None
    status: str | None = None
    severity: str | None = None
    message: str | None = None
    created_at: datetime | None = None


class CameraSchema(BaseModel):
    id: int | None = None
    camera_id: str
    latitude: float | None = None
    longitude: float | None = None
    orientation: int | None = None
    road_segment: str | None = None


class AnalyticsPayload(BaseModel):
    calculation_timestamp: datetime | None = None
    time_window: str | None = None
    sample_count: int = 0
    confidence: str | None = None
    values: dict[str, Any] = Field(default_factory=dict)
