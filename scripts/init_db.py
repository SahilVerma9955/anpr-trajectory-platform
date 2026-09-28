#!/usr/bin/env python3
"""Initialize the SQLite database and optionally seed demo cameras."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.database.models import Base, Camera


def init_database() -> None:
    """Create all tables in the configured database."""
    engine = create_engine(settings.database_url, future=True)
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized: {settings.database_url}")
    return engine


def seed_demo_cameras(engine) -> None:
    """Seed demo camera locations."""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        demo_cameras = [
            {"camera_id": "camera_01", "latitude": 28.6139, "longitude": 77.2090, "orientation": 90, "road_segment": "demo-road-1"},
            {"camera_id": "camera_02", "latitude": 28.6200, "longitude": 77.2150, "orientation": 180, "road_segment": "demo-road-2"},
            {"camera_id": "camera_03", "latitude": 28.6085, "longitude": 77.2065, "orientation": 270, "road_segment": "demo-road-3"},
        ]
        for data in demo_cameras:
            existing = db.query(Camera).filter(Camera.camera_id == data["camera_id"]).first()
            if not existing:
                camera = Camera(**data)
                db.add(camera)
        db.commit()
        print(f"Seeded {len(demo_cameras)} demo cameras.")
    finally:
        db.close()


if __name__ == "__main__":
    engine = init_database()
    seed_demo_cameras(engine)
    print("Database setup complete.")
