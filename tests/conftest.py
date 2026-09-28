"""Test fixtures and utilities."""

import pytest
from pathlib import Path
from datetime import datetime, timezone


@pytest.fixture
def sample_detections():
    return [
        {"normalized_plate": "DL01AB1234", "confidence": 0.95, "center": (100.0, 200.0)},
        {"normalized_plate": "MH12CD5678", "confidence": 0.87, "center": (200.0, 300.0)},
        {"normalized_plate": "DL01AB1234", "confidence": 0.91, "center": (110.0, 210.0)},
    ]


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary directory structure for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "raw").mkdir()
    (data_dir / "processed").mkdir()
    (data_dir / "frames").mkdir()
    return data_dir
