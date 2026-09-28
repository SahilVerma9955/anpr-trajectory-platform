"""Validation logic for Indian license plates."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class PlateValidationResult:
    """Outcome of plate validation."""

    is_valid: bool
    normalized_text: str
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "normalized_text": self.normalized_text,
            "reason": self.reason,
        }


def normalize_plate_text(value: str) -> str:
    """Normalize OCR text to a usable Indian plate format."""
    cleaned = re.sub(r"[^A-Z0-9]", "", str(value).upper().replace("-", "").replace(" ", ""))
    return cleaned


def validate_plate_text(value: str) -> PlateValidationResult:
    """Validate common Indian number-plate shapes without rejecting unusual but plausible values too harshly."""
    normalized = normalize_plate_text(value)
    if not normalized:
        return PlateValidationResult(False, "", "empty_plate")

    if len(normalized) < 8 or len(normalized) > 12:
        return PlateValidationResult(False, normalized, "length_out_of_range")

    # Common Indian plate patterns: DL01AB1234, MH12CD5678, UP32AA1234
    pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$"
    if re.fullmatch(pattern, normalized):
        return PlateValidationResult(True, normalized, "valid")

    # Some plates may have state code + district + letters + digits with 10 total chars.
    if re.fullmatch(r"^[A-Z]{2}[0-9]{2}[A-Z]{2,3}[0-9]{3,5}$", normalized):
        return PlateValidationResult(True, normalized, "valid_alternative_pattern")

    # A permissive fallback: allow plates with at least 2 letters + 2 digits + 4+ trailing alnum.
    if re.fullmatch(r"^[A-Z]{2,3}[0-9]{2,3}[A-Z0-9]{4,8}$", normalized):
        return PlateValidationResult(True, normalized, "permissive_match")

    return PlateValidationResult(False, normalized, "pattern_mismatch")
