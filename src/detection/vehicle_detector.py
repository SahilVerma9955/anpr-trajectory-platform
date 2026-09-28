"""Detection package for vehicles and plate analysis."""

from .plate_detector import PlateDetector
from .unified_detector import UnifiedDetector
from .vehicle_detector import VehicleDetector

__all__ = ["VehicleDetector", "PlateDetector", "UnifiedDetector"]
