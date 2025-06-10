"""Utility functions for patient matching."""
import re
from typing import List, Dict, Any
from datetime import datetime

def normalize_string(s: str, fieldName: str) -> str:
    """Normalize string for comparison: lowercase, remove punctuation/whitespace."""
    if fieldName == "DOB":
        return _normalize_date(s)
    elif fieldName == "PhoneNumber":
        return _normalize_phone(s)
    elif fieldName == "Address":
        return _normalize_address(s)
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
    
def extract_base_address(addr: str) -> str:
    """Extract base address without suite/apartment number."""
    if not addr:
        return ""
    
    # Remove leading zeros from house numbers first
    addr = re.sub(r'^0+(\d)', r'\1', addr)
    
    # Remove suite/apartment patterns
    # Patterns like: "apt 123", "suite 45", "ste a", "#205"
    base = re.sub(r'\b(apt|ste|suite|apartment|unit|#)\s*\w+\b', '', addr, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    base = re.sub(r'\s+', ' ', base).strip()
    
    return base
    
def _normalize_date(date_str: str) -> str:
    """Normalize date from DD-MMM-YYYY to YYYY-MM-DD format, leave others unchanged."""
    if not date_str:
        return ""
        
    
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

def _normalize_phone(phone_str: str) -> str:
    """Normalize phone number to digits only."""
    if not phone_str:
        return ""
    return re.sub(r'\D', '', phone_str)

def _normalize_address(addr_str: str) -> str:
    """Normalize address for comparison."""
    if not addr_str:
        return ""
    
    # Convert to lowercase and clean up
    normalized = addr_str.lower().strip()
    
    # Standardize common abbreviations
    replacements = {
        r'\bstreet\b': 'st',
        r'\bstret\b': 'st',  # common typo
        r'\bavenue\b': 'ave',
        r'\bboulevard\b': 'blvd',
        r'\bdrive\b': 'dr',
        r'\bplace\b': 'pl',
        r'\bcourt\b': 'ct',
        r'\bapartment\b': 'apt',
        r'\bsuite\b': 'ste',
        r'\bnorth\b': 'n',
        r'\bsouth\b': 's',
        r'\beast\b': 'e',
        r'\bwest\b': 'w',
    }
    
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    
    # Remove extra spaces and punctuation
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized