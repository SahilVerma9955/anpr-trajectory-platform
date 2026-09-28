"""Main FastAPI application for the ANPR platform."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.config import settings
from src.database.database import get_db, engine
from src.database.models import Base
from src.database.crud import Crud
from src.database.schemas import (
    AlertSchema,
    AnalyticsPayload,
    CameraSchema,
    VideoSchema,
    VehicleSchema,
)
from src.analytics import (
    CongestionCalculator,
    ODMatrix,
    SpeedCalculator,
    TrafficDensity,
    TrafficFlow,
    TrafficHeatmap,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ANPR Trajectory Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(x_api_key: str | None = Header(None)) -> str | None:
    """Verify API key if authentication is enabled."""
    if not settings.api_auth_enabled:
        return None
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return x_api_key


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "anpr-platform", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/videos")
async def list_videos(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """List all videos in the system."""
    crud = Crud(db)
    videos = crud.list_videos()
    return {"count": len(videos), "videos": [VideoSchema.model_validate({"id": v.id, "video_id": v.video_id, "camera_id": v.camera_id, "source_path": v.source_path, "frame_count": v.frame_count, "fps": v.fps, "width": v.width, "height": v.height, "duration_seconds": v.duration_seconds}).model_dump() for v in videos]}


@app.get("/api/cameras")
async def list_cameras(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """List all cameras."""
    crud = Crud(db)
    cameras = crud.list_cameras()
    return {"count": len(cameras), "cameras": [CameraSchema.model_validate({"id": c.id, "camera_id": c.camera_id, "latitude": c.latitude, "longitude": c.longitude, "orientation": c.orientation, "road_segment": c.road_segment}).model_dump() for c in cameras]}


@app.get("/api/vehicles")
async def list_vehicles(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """List all detected vehicles."""
    vehicles = db.query("vehicles").all()
    return {"count": len(vehicles) if vehicles else 0, "message": "Vehicle listing endpoint"}


@app.get("/api/vehicles/{plate}")
async def get_vehicle(plate: str, db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """Get vehicle details by normalized plate."""
    crud = Crud(db)
    vehicle = crud.get_vehicle_by_plate(plate)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleSchema.model_validate({"id": vehicle.id, "track_id": vehicle.track_id, "camera_id": vehicle.camera_id, "plate": vehicle.plate, "normalized_plate": vehicle.normalized_plate, "vehicle_class": vehicle.vehicle_class, "confidence": vehicle.confidence}).model_dump()


@app.get("/api/vehicles/{plate}/detections")
async def get_vehicle_detections(plate: str, db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """Get all detections for a vehicle plate."""
    return {"plate": plate, "detections": [], "message": "Detections endpoint"}


@app.get("/api/trajectories/{plate}")
async def get_trajectory(plate: str, db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """Get vehicle trajectory across cameras."""
    return {
        "plate": plate,
        "trajectory": {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {"plate": plate}, "geometry": {"type": "LineString", "coordinates": []}}],
        },
        "message": "Trajectory endpoint",
    }


@app.get("/api/analytics/density")
async def analytics_density(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> AnalyticsPayload:
    """Calculate traffic density."""
    density_data = TrafficDensity.calculate([], time_window_seconds=60)
    return AnalyticsPayload(
        calculation_timestamp=datetime.now(timezone.utc),
        time_window="60s",
        sample_count=0,
        confidence="no_data",
        values=density_data,
    )


@app.get("/api/analytics/flow")
async def analytics_flow(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> AnalyticsPayload:
    """Calculate traffic flow."""
    flow_data = TrafficFlow.calculate([], time_window_seconds=60)
    return AnalyticsPayload(
        calculation_timestamp=datetime.now(timezone.utc),
        time_window="60s",
        sample_count=0,
        confidence="no_data",
        values=flow_data,
    )


@app.get("/api/analytics/speed")
async def analytics_speed(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> AnalyticsPayload:
    """Calculate average speed from trajectories."""
    return AnalyticsPayload(
        calculation_timestamp=datetime.now(timezone.utc),
        time_window="all",
        sample_count=0,
        confidence="no_data",
        values={"average_speed_kmh": 0.0},
    )


@app.get("/api/analytics/congestion")
async def analytics_congestion(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> AnalyticsPayload:
    """Calculate congestion index."""
    congestion_data = CongestionCalculator.calculate(0.0, free_flow_speed_kmh=settings.free_flow_speed_kmh)
    return AnalyticsPayload(
        calculation_timestamp=datetime.now(timezone.utc),
        time_window="real-time",
        sample_count=0,
        confidence="no_data",
        values=congestion_data,
    )


@app.get("/api/analytics/heatmap")
async def analytics_heatmap(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> AnalyticsPayload:
    """Generate traffic heatmap."""
    heatmap = TrafficHeatmap.generate([], grid_size=10, image_width=1920, image_height=1080)
    return AnalyticsPayload(
        calculation_timestamp=datetime.now(timezone.utc),
        time_window="all",
        sample_count=len(heatmap),
        confidence="medium",
        values={"heatmap_points": heatmap},
    )


@app.get("/api/analytics/od-matrix")
async def analytics_od_matrix(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> AnalyticsPayload:
    """Origin-destination matrix."""
    od = ODMatrix.compute([])
    return AnalyticsPayload(
        calculation_timestamp=datetime.now(timezone.utc),
        time_window="all",
        sample_count=len(od),
        confidence="medium",
        values={"od_matrix": od},
    )


@app.get("/api/alerts")
async def list_alerts(db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """List active alerts."""
    crud = Crud(db)
    alerts = crud.list_alerts()
    return {"count": len(alerts), "alerts": [AlertSchema.model_validate({"id": a.id, "plate": a.plate, "normalized_plate": a.normalized_plate, "status": a.status, "severity": a.severity, "message": a.message, "created_at": a.created_at}).model_dump() for a in alerts]}


@app.post("/api/alerts/blacklist")
async def add_blacklist(plate: str, reason: str | None = None, db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """Add a plate to the watchlist."""
    crud = Crud(db)
    entry = crud.add_blacklist(plate, plate.upper(), reason or "manual_add")
    return {"id": entry.id, "plate": entry.plate, "reason": entry.reason}


@app.delete("/api/alerts/blacklist/{plate}")
async def remove_blacklist(plate: str, db: Session = Depends(get_db), _: str | None = Depends(verify_api_key)) -> dict[str, Any]:
    """Remove a plate from the watchlist."""
    crud = Crud(db)
    success = crud.remove_blacklist(plate.upper())
    if not success:
        raise HTTPException(status_code=404, detail="Plate not found in blacklist")
    return {"success": True, "plate": plate}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
