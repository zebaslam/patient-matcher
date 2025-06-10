"""Utility functions for patient matching."""
import re
from typing import List, Dict, Any

def normalize_string(s: str) -> str:
    """Normalize string for comparison: lowercase, remove punctuation/whitespace."""
    if not s:
        return ""
    normalized = re.sub(r'[^\w\s]', '', str(s).lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def add_unique_ids(patients: List[Dict[str, Any]], prefix: str) -> None:
    """Internal helper to add stable unique IDs to patient records."""
    for i, patient in enumerate(patients):
        patient['Id'] = f'{prefix}-{i}'

def get_patient_id(patient: Dict[str, Any]) -> str:
    """Get the actual patient ID from the record."""
    # Check for both possible ID field names
    if 'InternalPatientId' in patient:
        return patient['InternalPatientId']
    elif 'ExternalPatientId' in patient:
        return patient['ExternalPatientId']
    else:
        # Fallback to generated ID if no real ID exists
        return patient.get('Id', 'UNKNOWN')