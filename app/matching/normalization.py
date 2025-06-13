"""Data normalization functions for patient matching."""

import re
import logging
from datetime import datetime

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
    "lane": "ln",
    "unit": "u",
    "isle": "island",
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


def normalize_date(date_str: str) -> str:
    """Normalize date from DD-MMM-YYYY to YYYY-MM-DD format, leave others unchanged."""
    if not date_str:
        return ""

    date_str = date_str.strip()

    # Check if it matches DD-MMM-YYYY pattern (e.g., "02-Dec-1978")
    if re.match(r"^\d{1,2}-[A-Za-z]{3}-\d{4}$", date_str):
        try:
            parsed_date = datetime.strptime(date_str, "%d-%b-%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            logging.warning(
                "Could not parse date '%s' despite matching pattern. Expected format: DD-MMM-YYYY.",
                date_str,
            )
            return date_str

    # Not DD-MMM-YYYY format, return as-is
    return date_str


def _normalize_phone(phone_str: str) -> str:
    """Normalize phone number to digits only."""
    return re.sub(r"\D", "", phone_str) if phone_str else ""


def extract_base_address(addr: str) -> str:
    """
    Extract base address, removing leading zeros from house numbers,
    trailing punctuation, and apartment/unit/suite information.
    """
    if not addr:
        return ""

    addr = addr.strip()

    # If address starts with apartment/unit/suite, return empty string
    if re.match(r"^(Apt|Apartment|Suite|Ste|Unit|#)\b", addr, flags=re.IGNORECASE):
        return ""

    # If address is just a number (possibly with leading zeros)
    if re.fullmatch(r"0*\d+", addr):
        return str(int(addr))

    # Remove leading zeros from house numbers (including hyphenated, e.g., 0456-B)
    addr = re.sub(r"^0+(\d[\w\-]*)", r"\1", addr)

    # Remove apartment/unit/suite info and everything after
    addr = re.split(
        r"\b(?:Apt|Apartment|Suite|Ste|Unit|#)\b", addr, flags=re.IGNORECASE
    )[0]

    # Remove any trailing punctuation and whitespace (including spaces before punctuation)
    addr = re.sub(r"[\s,\.]+$", "", addr)

    # Collapse spaces and trim
    return re.sub(r"\s+", " ", addr).strip()


def _normalize_address(addr_str: str) -> str:
    """Normalize address for comparison."""
    if not addr_str:
        return ""

    # Special case: if address is just "APT 5", "Suite 2", etc.
    m = re.match(
        r"^(apt|apartment|suite|ste|unit|#)\s+(\w+)$", addr_str.strip(), re.IGNORECASE
    )
    if m:
        abbrev = REPLACEMENTS_LOWER.get(m.group(1).lower(), m.group(1).lower())
        return f"{abbrev} {m.group(2).lower()}"

    # Special case: if address is "<number> <suite-type>"
    m2 = re.match(
        r"^(\d+)\s+(suite|ste|apartment|apt|unit|#)$", addr_str.strip(), re.IGNORECASE
    )
    if m2:
        abbrev = REPLACEMENTS_LOWER.get(m2.group(2).lower(), m2.group(2).lower())
        return f"{m2.group(1)} {abbrev}"

    # Special case: if address is "<number> <directional> <suite-type>"
    m3 = re.match(
        r"^(\d+)\s+(north|south|east|west)\s+(suite|ste|apartment|apt|unit|#)$",
        addr_str.strip(),
        re.IGNORECASE,
    )
    if m3:
        abbrev_dir = REPLACEMENTS_LOWER.get(m3.group(2).lower(), m3.group(2).lower())
        abbrev_suite = REPLACEMENTS_LOWER.get(m3.group(3).lower(), m3.group(3).lower())
        return f"{m3.group(1)} {abbrev_dir} {abbrev_suite}"

    # Use base address (strip apartment/unit/suite)
    normalized = extract_base_address(addr_str).lower().strip()

    # Standardize common abbreviations
    normalized = REPLACEMENTS_PATTERN.sub(
        lambda match: REPLACEMENTS_LOWER[match.group(0).lower()], normalized
    )

    # Remove extra spaces and punctuation, but preserve hyphens
    normalized = re.sub(r"[^\w\s-]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


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
    match field_name.casefold():
        case "dob":
            return normalize_date(s)
        case "phone_number":
            return _normalize_phone(s)
        case "address":
            return _normalize_address(s)
        case _:
            # General string normalization
            normalized = re.sub(r"[^\w\s]", "", str(s).lower())
            return re.sub(r"\s+", " ", normalized).strip()
