"""Utility functions for patient matching."""

import re
import time
import logging
from typing import List, Dict, Any
from functools import wraps

# ============================================================================
# CONSTANTS
# ============================================================================

FALLBACK_PATIENT_ID = "UNKNOWN"

# Address standardization mappings
REPLACEMENTS = {
    "street": "st",
    "stret": "st",  # common typo
    "avenue": "ave",
    "boulevard": "blvd",
    "drive": "dr",
    "place": "pl",
    "court": "ct",
    "apartment": "apt",
    "suite": "ste",
    "north": "n",
    "south": "s",
    "east": "e",
    "west": "w",
}
REPLACEMENTS_LOWER = {key.lower(): value for key, value in REPLACEMENTS.items()}
REPLACEMENTS_PATTERN = re.compile(
    r"\b(" + "|".join(REPLACEMENTS_LOWER.keys()) + r")\b", flags=re.IGNORECASE
)

# ============================================================================
# PATIENT RECORD UTILITIES
# ============================================================================


def add_unique_ids(patients: List[Dict[str, Any]], prefix: str) -> None:
    """Add stable unique IDs to patient records."""
    for i, patient in enumerate(patients):
        patient["Id"] = f"{prefix}-{i}"


def get_patient_id(patient: Dict[str, Any]) -> str:
    """Get the actual patient ID from the record."""
    return (
        patient.get("InternalPatientId")
        or patient.get("ExternalPatientId")
        or patient.get("Id", FALLBACK_PATIENT_ID)
    )


# ============================================================================
# Decorators
# ============================================================================


def log_elapsed_time(func):
    """Decorator that logs the elapsed time of the decorated function or method."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time

        # Try to get class name if this is a method
        if args and hasattr(args[0], "__class__"):
            class_name = args[0].__class__.__name__
            func_name = f"{class_name}.{func.__name__}"
        else:
            func_name = func.__name__

        logging.info("%s completed in %.3f seconds.", func_name, elapsed)
        return result

    return wrapper
