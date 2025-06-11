"""
Constants for patient matching normalization fields.

This module defines precomputed normalization field mappings used in the patient matcher application.
"""

from typing import Dict

PRECOMPUTED_NORMALIZATION_FIELDS: Dict[str, str] = {
    "DOB": "DOBNormalized",
    "Sex": "SexNormalized",
}
