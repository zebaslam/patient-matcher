"""
Constants for patient matching normalization fields.

This module defines precomputed normalization field mappings used in the patient matcher application.
"""

from typing import Dict

PRECOMPUTED_NORMALIZATION_FIELDS: Dict[str, str] = {
    "dob": "dob_norm",
    "sex": "sex_norm",
}

NORMALIZED_FIELDS = {
    **PRECOMPUTED_NORMALIZATION_FIELDS,
    "first_name": "first_name_norm",
    "last_name": "last_name_norm",
    "address": "address_norm",
    "city": "city_norm",
    "zipcode": "zipcode_norm",
    "phone_number": "phone_number_norm",
    # Add more fields as needed
}

CRITICAL_FIELDS = {"dob", "sex", "first_name"}

DEFAULT_SIMILARITY = 0.0
DEFAULT_PENALTY = 0.0
JARO_THRESHOLD = 0.7
