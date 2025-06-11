"""
Constants for patient matching normalization fields.

This module defines precomputed normalization field mappings used in the patient matcher application.
"""

from typing import Dict

PRECOMPUTED_NORMALIZATION_FIELDS: Dict[str, str] = {
    "dob": "DOBNormalized",
    "sex": "SexNormalized",
}

CRITICAL_FIELDS = {"dob", "first_name", "address"}

DEFAULT_SIMILARITY = 0.0
DEFAULT_PENALTY = 0.0
