"""Utility functions for patient matching."""
import re
import logging
from typing import List, Dict, Any
from datetime import datetime

# Constants
FALLBACK_PATIENT_ID = 'UNKNOWN'

# Standardize common abbreviations (constant, only initialized once)
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


def add_unique_ids(patients: List[Dict[str, Any]], prefix: str) -> None:
    """Internal helper to add stable unique IDs to patient records."""
    for i, patient in enumerate(patients):
        patient['Id'] = f'{prefix}-{i}'


def get_patient_id(patient: Dict[str, Any]) -> str:
    """Get the actual patient ID from the record."""
    return (patient.get('InternalPatientId') or 
            patient.get('ExternalPatientId') or 
            patient.get('Id', FALLBACK_PATIENT_ID))


def extract_base_address(addr: str) -> str:
    """
    Extract base address, removing leading zeros from house numbers, 
    trailing punctuation, and apartment/unit/suite information.
    """
    if not addr:
        return ""

    # Remove leading zeros from house numbers
    addr = re.sub(r'^0+(\d[\w\-]*)', r'\1', addr)
    
    # Remove trailing punctuation
    addr = re.sub(r'[.,]+$', '', addr)

    # Remove apartment/unit/suite information
    addr = re.split(
        r'\b(?:Apt|Apartment|Suite|Ste|Unit|#)\b', 
        addr, 
        flags=re.IGNORECASE
    )[0]

    # Collapse multiple spaces and trim
    return re.sub(r'\s+', ' ', addr).strip()


def normalize_date(date_str: str) -> str:
    """Normalize date from DD-MMM-YYYY to YYYY-MM-DD format, leave others unchanged."""
    if not date_str:
        return ""
    
    date_str = date_str.strip()
    
    # Check if it matches DD-MMM-YYYY pattern (e.g., "02-Dec-1978")
    if re.match(r'^\d{1,2}-[A-Za-z]{3}-\d{4}$', date_str):
        try:
            parsed_date = datetime.strptime(date_str, "%d-%b-%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            logging.warning(
                f"Could not parse date '{date_str}' despite matching pattern. "
                f"Expected format: DD-MMM-YYYY."
            )
            return date_str
    
    # Not DD-MMM-YYYY format, return as-is
    return date_str


def _normalize_phone(phone_str: str) -> str:
    """Normalize phone number to digits only."""
    if not phone_str:
        return ""
    return re.sub(r'\D', '', phone_str)


def _normalize_address(addr_str: str) -> str:
    """Normalize address for comparison."""
    if not addr_str:
        return ""
    
    # Use base address (strip apartment/unit/suite)
    addr_str = extract_base_address(addr_str)
    
    # Convert to lowercase and clean up
    normalized = addr_str.lower().strip()
    
    # Standardize common abbreviations
    normalized = REPLACEMENTS_PATTERN.sub(
        lambda match: REPLACEMENTS_LOWER[match.group(0).lower()], 
        normalized
    )
    
    # Remove extra spaces and punctuation, but preserve hyphens
    normalized = re.sub(r'[^\w\s-]', ' ', normalized)
    return re.sub(r'\s+', ' ', normalized).strip()


def normalize_string(s: str, field_name: str) -> str:
    """
    Normalize string for comparison based on the field type.

    Args:
        s: The input string to normalize.
        field_name: The name of the field to normalize. Expected values are:
            - "DOB": Normalize date strings (e.g., "02-Dec-1978" -> "1978-12-02").
            - "PhoneNumber": Normalize phone numbers to digits only.
            - "Address": Normalize addresses by removing suite/apartment/unit 
              numbers and standardizing abbreviations.

    Returns:
        The normalized string.
    """
    if field_name == "DOB":
        return normalize_date(s)
    elif field_name == "PhoneNumber":
        return _normalize_phone(s)
    elif field_name == "Address":
        return _normalize_address(s)
    else:
        # General string normalization
        normalized = re.sub(r'[^\w\s]', '', str(s).lower())
        return re.sub(r'\s+', ' ', normalized).strip()