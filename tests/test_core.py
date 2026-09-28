"""Test suite for the ANPR platform."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from src.ocr.plate_validator import validate_plate_text, normalize_plate_text
from src.analytics import CongestionCalculator, TrafficDensity, TrafficFlow, SpeedCalculator, TrafficHeatmap, ODMatrix
from src.tracking.multi_camera_fusion import haversine_km, MultiCameraFusion
from src.tracking.trajectory import Trajectory, TrajectoryBuilder


class TestPlateValidation:
    """Test Indian plate normalization and validation."""

    def test_normalize_uppercase(self) -> None:
        result = normalize_plate_text("dl01ab1234")
        assert result == "DL01AB1234"

    def test_normalize_remove_spaces(self) -> None:
        result = normalize_plate_text("DL 01 AB 1234")
        assert result == "DL01AB1234"

    def test_normalize_remove_hyphens(self) -> None:
        result = normalize_plate_text("DL-01-AB-1234")
        assert result == "DL01AB1234"

    def test_validate_standard_plate(self) -> None:
        validation = validate_plate_text("DL01AB1234")
        assert validation.is_valid is True
        assert validation.normalized_text == "DL01AB1234"

    def test_validate_mh_plate(self) -> None:
        validation = validate_plate_text("MH12CD5678")
        assert validation.is_valid is True

    def test_validate_up_plate(self) -> None:
        validation = validate_plate_text("UP32AA1234")
        assert validation.is_valid is True

    def test_reject_empty(self) -> None:
        validation = validate_plate_text("")
        assert validation.is_valid is False
        assert validation.reason == "empty_plate"

    def test_reject_too_short(self) -> None:
        validation = validate_plate_text("DL01")
        assert validation.is_valid is False

    def test_reject_too_long(self) -> None:
        validation = validate_plate_text("DL01AB1234EXTRA")
        assert validation.is_valid is False


class TestAnalytics:
    """Test traffic analytics calculations."""

    def test_density_empty(self) -> None:
        result = TrafficDensity.calculate([])
        assert result["vehicle_count"] == 0

    def test_density_multiple(self) -> None:
        detections = [
            {"normalized_plate": "DL01AB1234"},
            {"normalized_plate": "DL01AB1234"},
            {"normalized_plate": "MH12CD5678"},
        ]
        result = TrafficDensity.calculate(detections)
        assert result["vehicle_count"] == 2

    def test_flow_empty(self) -> None:
        result = TrafficFlow.calculate([])
        assert result["vehicles_per_minute"] == 0.0

    def test_flow_calculation(self) -> None:
        detections = [{"normalized_plate": f"PL{i:04d}"} for i in range(12)]
        result = TrafficFlow.calculate(detections, time_window_seconds=60)
        assert result["vehicles_per_minute"] > 0.0

    def test_speed_from_trajectory(self) -> None:
        speed_kmh = SpeedCalculator.calculate_from_trajectory(distance_meters=100.0, duration_seconds=10.0)
        assert speed_kmh == pytest.approx(36.0, rel=0.01)

    def test_speed_zero_duration(self) -> None:
        speed_kmh = SpeedCalculator.calculate_from_trajectory(distance_meters=100.0, duration_seconds=0.0)
        assert speed_kmh == 0.0

    def test_congestion_free_flow(self) -> None:
        result = CongestionCalculator.calculate(average_speed_kmh=50.0, free_flow_speed_kmh=50.0)
        assert result["congestion_index"] == pytest.approx(0.0, abs=0.01)
        assert result["status"] == "free_flow"

    def test_congestion_heavy(self) -> None:
        result = CongestionCalculator.calculate(average_speed_kmh=10.0, free_flow_speed_kmh=50.0)
        assert result["congestion_index"] > 0.75
        assert result["status"] == "congested"

    def test_heatmap_empty(self) -> None:
        result = TrafficHeatmap.generate([])
        assert len(result) == 0

    def test_heatmap_single_cell(self) -> None:
        detections = [{"center": (960, 540)} for _ in range(5)]
        result = TrafficHeatmap.generate(detections, grid_size=2, image_width=1920, image_height=1080)
        assert len(result) > 0

    def test_od_matrix_empty(self) -> None:
        result = ODMatrix.compute([])
        assert len(result) == 0

    def test_od_matrix_simple(self) -> None:
        trajectories = [{"camera_sequence": ["camera_01", "camera_02"]}]
        result = ODMatrix.compute(trajectories)
        assert "camera_01→camera_02" in result
        assert result["camera_01→camera_02"] == 1


class TestTracking:
    """Test trajectory and tracking logic."""

    def test_trajectory_append(self) -> None:
        traj = Trajectory(plate="DL01AB1234")
        timestamp = datetime.now(timezone.utc)
        traj.append(timestamp, 100.0, 200.0, "camera_01")
        assert len(traj.points) == 1
        assert traj.points[0].x == 100.0

    def test_trajectory_sort(self) -> None:
        traj = Trajectory()
        now = datetime.now(timezone.utc)
        traj.append(now, 100.0, 200.0)
        traj.append(now.replace(microsecond=0), 150.0, 250.0)
        traj.sort()
        assert len(traj.points) == 2

    def test_trajectory_approximate_distance(self) -> None:
        traj = Trajectory()
        traj.append(datetime.now(timezone.utc), 0.0, 0.0)
        traj.append(datetime.now(timezone.utc), 3.0, 4.0)
        distance = traj.approximate_distance()
        assert distance == pytest.approx(5.0, rel=0.01)

    def test_haversine_distance(self) -> None:
        distance = haversine_km(28.6139, 77.2090, 28.6200, 77.2150)
        assert 8 < distance < 10

    def test_multi_camera_plausible_link_bad_similarity(self) -> None:
        fusion = MultiCameraFusion()
        result = fusion.plausible_link(
            normalized_plate_similarity=0.5,
            ocr_confidence=0.3,
            time_gap_seconds=60.0,
            camera_a="camera_01",
            camera_b="camera_02",
        )
        assert result is False

    def test_multi_camera_plausible_link_good(self) -> None:
        fusion = MultiCameraFusion()
        result = fusion.plausible_link(
            normalized_plate_similarity=0.95,
            ocr_confidence=0.8,
            time_gap_seconds=120.0,
            camera_a="camera_01",
            camera_b="camera_02",
        )
        assert result is True


class TestAPI:
    """Test FastAPI endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from src.api.main import app

        return TestClient(app)

    def test_health(self, client) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_list_cameras_no_auth(self, client) -> None:
        response = client.get("/api/cameras")
        assert response.status_code in (200, 401, 403)

    def test_list_videos_no_auth(self, client) -> None:
        response = client.get("/api/videos")
        assert response.status_code in (200, 401, 403)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
