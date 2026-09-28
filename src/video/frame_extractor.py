"""Video processing utilities package."""

from .frame_extractor import extract_frames
from .metadata import VideoMetadata, extract_video_metadata

__all__ = ["VideoMetadata", "extract_video_metadata", "extract_frames"]
