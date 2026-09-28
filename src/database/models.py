"""Database models for the ANPR platform."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Camera(Base):
    __tablename__ = "cameras"
    __table_args__ = (UniqueConstraint("camera_id", name="uq_camera_id"),)

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(255), nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    orientation = Column(Integer, nullable=True)
    road_segment = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(255), nullable=False, unique=True, index=True)
    camera_id = Column(String(255), nullable=True, index=True)
    source_path = Column(String(500), nullable=True)
    frame_count = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(String(255), nullable=True, index=True)
    camera_id = Column(String(255), nullable=True, index=True)
    plate = Column(String(255), nullable=True, index=True)
    normalized_plate = Column(String(255), nullable=True, index=True)
    vehicle_class = Column(String(128), nullable=True)
    first_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    last_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    confidence = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True, index=True)
    camera_id = Column(String(255), nullable=True, index=True)
    track_id = Column(String(255), nullable=True, index=True)
    normalized_plate = Column(String(255), nullable=True, index=True)
    vehicle_confidence = Column(Float, nullable=True)
    bbox_json = Column(JSON, nullable=True)
    center_x = Column(Float, nullable=True)
    center_y = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    metadata_json = Column(JSON, nullable=True)


class OCRObservation(Base):
    __tablename__ = "ocr_observations"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(String(255), nullable=True, index=True)
    camera_id = Column(String(255), nullable=True, index=True)
    raw_text = Column(Text, nullable=True)
    normalized_plate = Column(String(255), nullable=True, index=True)
    confidence = Column(Float, nullable=True)
    validation_status = Column(Boolean, nullable=True)
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    metadata_json = Column(JSON, nullable=True)


class Trajectory(Base):
    __tablename__ = "trajectories"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(String(255), nullable=True, index=True)
    normalized_plate = Column(String(255), nullable=True, index=True)
    camera_sequence = Column(JSON, nullable=True)
    route_points = Column(JSON, nullable=True)
    distance_meters = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    avg_speed_kmh = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class TrajectoryPoint(Base):
    __tablename__ = "trajectory_points"

    id = Column(Integer, primary_key=True, index=True)
    trajectory_id = Column(Integer, ForeignKey("trajectories.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)
    camera_id = Column(String(255), nullable=True, index=True)


class BlacklistEntry(Base):
    __tablename__ = "blacklist_entries"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String(255), nullable=False, index=True)
    normalized_plate = Column(String(255), nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    alert_enabled = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String(255), nullable=True, index=True)
    normalized_plate = Column(String(255), nullable=True, index=True)
    status = Column(String(50), default="open", index=True)
    severity = Column(String(50), nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(255), nullable=True, index=True)
    road_segment = Column(String(255), nullable=True)
    metric_name = Column(String(255), nullable=True, index=True)
    metric_value = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    metadata_json = Column(JSON, nullable=True)
