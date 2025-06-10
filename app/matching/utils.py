"""Utility functions for patient matching."""
import re
from typing import List, Dict, Any
from datetime import datetime

def normalize_string(s: str, fieldName: str) -> str:
    """Normalize string for comparison: lowercase, remove punctuation/whitespace."""
    if fieldName == "DOB":
        return _normalize_date(s)
    else:
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
    
def _normalize_date(date_str: str) -> str:
    """Normalize date from DD-MMM-YYYY to YYYY-MM-DD format, leave others unchanged."""

    date_str = date_str.strip()
    
    # Check if it matches DD-MMM-YYYY pattern (e.g., "02-Dec-1978")
    # Pattern: digits-letters-digits
    if re.match(r'^\d{1,2}-[A-Za-z]{3}-\d{4}$', date_str):
        try:
            # Parse DD-MMM-YYYY format
            parsed_date = datetime.strptime(date_str, "%d-%b-%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            print(f"Warning: Could not parse date despite matching pattern: {date_str}")
            return date_str
    else:
        # Not DD-MMM-YYYY format, return as-is
        return date_str