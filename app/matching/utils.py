"""Utility functions for patient matching."""
import re
from typing import List, Dict, Any

# ============================================================================
# CONSTANTS
# ============================================================================

FALLBACK_PATIENT_ID = 'UNKNOWN'

# Address standardization mappings
REPLACEMENTS = {
    'street': 'st',
    'stret': 'st',  # common typo
    'avenue': 'ave',
    'boulevard': 'blvd',
    'drive': 'dr',
    'place': 'pl',
    'court': 'ct',
    'apartment': 'apt',
    'suite': 'ste',
    'north': 'n',
    'south': 's',
    'east': 'e',
    'west': 'w',
}
REPLACEMENTS_LOWER = {key.lower(): value for key, value in REPLACEMENTS.items()}
REPLACEMENTS_PATTERN = re.compile(
    r'\b(' + '|'.join(REPLACEMENTS_LOWER.keys()) + r')\b', 
    flags=re.IGNORECASE
)

# ============================================================================
# PATIENT RECORD UTILITIES
# ============================================================================

def add_unique_ids(patients: List[Dict[str, Any]], prefix: str) -> None:
    """Add stable unique IDs to patient records."""
    for i, patient in enumerate(patients):
        patient['Id'] = f'{prefix}-{i}'

def get_patient_id(patient: Dict[str, Any]) -> str:
    """Get the actual patient ID from the record."""
    return (patient.get('InternalPatientId') or 
            patient.get('ExternalPatientId') or 
            patient.get('Id', FALLBACK_PATIENT_ID))
