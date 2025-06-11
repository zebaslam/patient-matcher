"""Field-specific similarity functions for patient matching."""
from typing import Dict, Any, Optional
from app.config import (
    FIRST_NAME_MIDDLE_NAME, FIRST_NAME_MATCH, PHONE_PARTIAL_MATCH, GENERAL_SIMILARITY_MULTIPLIER
)
from .similarity import similarity_ratio, token_overlap_score, jaro_winkler_similarity
from .utils import _normalize_phone, normalize_string

def _check_basic_similarity(val1: str, val2: str) -> Optional[float]:
    """Check for basic similarity cases. Returns None if further processing needed."""
    if not val1 or not val2:
        return 0.0
    if val1 == val2:
        return 1.0
    return None

def calculate_field_similarity(first_field: str, second_field: str, field_type: str, field_name: str) -> float:
    """Calculate similarity between two field values based on field type."""
    try:
        # Normalize both fields first
        norm1 = normalize_string(first_field, field_name)
        norm2 = normalize_string(second_field, field_name)

        # Field-specific similarity functions (now use normalized values)
        field_handlers = {
            "PhoneNumber": phone_similarity,
            "Address": address_similarity,
        }
        if field_name in field_handlers:
            return field_handlers[field_name](norm1, norm2)

        # Check basic similarity cases
        basic_result = _check_basic_similarity(norm1, norm2)
        if basic_result is not None:
            return basic_result

        # Type-based similarity functions
        type_handlers = {
            "exact": lambda n1, n2: 0.0,
            "name": lambda n1, n2: _name_similarity(n1, n2, field_name),
            "general": _general_similarity
        }
        handler = type_handlers.get(field_type, type_handlers["general"])
        return handler(norm1, norm2)

    except Exception as e:
        print(f"Error calculating field similarity: {e}")
        return 0.0

def _name_similarity(norm1: str, norm2: str, field_name: str) -> float:
    """Handle name-type field similarity."""
    if field_name == "FirstName":
        return first_name_similarity(norm1, norm2)
    else:
         return last_name_similarity(norm1, norm2)

def _general_similarity(norm1: str, norm2: str) -> float:
    """Handle general-type field similarity."""
    if ' ' in norm1 or ' ' in norm2:
        token_score = token_overlap_score(norm1, norm2)
        similarity_score = similarity_ratio(norm1, norm2)
        return max(token_score, similarity_score * GENERAL_SIMILARITY_MULTIPLIER)
    else:
        return similarity_ratio(norm1, norm2)

def first_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity for first names, handling middle names."""
    # Normalize and tokenize
    tokens1 = name1.lower().split()
    tokens2 = name2.lower().split()

    # First name + middle name case
    if len(tokens1) != len(tokens2):
        shorter, longer = (tokens1, tokens2) if len(tokens1) < len(tokens2) else (tokens2, tokens1)
        if len(shorter) == 1 and len(longer) >= 1 and shorter[0] == longer[0]:
            return FIRST_NAME_MIDDLE_NAME

    # Same first name, different middle names
    if len(tokens1) >= 1 and len(tokens2) >= 1 and tokens1[0] == tokens2[0]:
        return FIRST_NAME_MATCH

    # Fuzzy match, but only return if above threshold
    sim = jaro_winkler_similarity(name1, name2)
    return sim if sim >= FIRST_NAME_MATCH else 0.0

def phone_similarity(phone1, phone2):
    """Calculate similarity for phone numbers, allowing for partial matches."""
    norm1 = _normalize_phone(phone1)
    norm2 = _normalize_phone(phone2)

    if not norm1 or not norm2:
        return 0.0

    if norm1 == norm2:
        return 1.0

    # Check if one is a suffix of the other (local number match)
    if norm1.endswith(norm2) or norm2.endswith(norm1):
        return PHONE_PARTIAL_MATCH  # Use the configured partial match score

    return 0.0
    
    
def address_similarity(norm1: str, norm2: str) -> float:
    """Stricter similarity between addresses, requiring street number and main name match."""

    # Quick check for exact match
    if norm1 == norm2:
        return 1.0

    # Extract street numbers and names
    def split_address(addr):
        tokens = addr.split()
        number = tokens[0] if tokens and tokens[0].isdigit() else ""
        # Use first two tokens as main street name for stricter match
        name = " ".join(tokens[1:3]).lower() if len(tokens) > 2 else " ".join(tokens[1:]).lower()
        return number, name

    num1, name1 = split_address(norm1)
    num2, name2 = split_address(norm2)

    # Require both street number and main name to match for high similarity
    if num1 and num2 and num1 == num2 and name1 == name2:
        return 1.0
    elif name1 == name2:
        return 0.7  # Same street name, different number
    elif num1 == num2:
        return 0.5  # Same number, different street name

    # Fallback to token overlap or ratio (very low similarity)
    token_score = token_overlap_score(norm1, norm2)
    similarity_score = similarity_ratio(norm1, norm2)
    return max(token_score, similarity_score * 0.5)

def has_gender_mismatch(patient1: Dict[str, Any], patient2: Dict[str, Any]) -> bool:
    """Check if patients have different genders."""
    sex1, sex2 = patient1.get('Sex'), patient2.get('Sex')
    return sex1 is not None and sex2 is not None and sex1 != sex2

def last_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity for last names."""
    sim = jaro_winkler_similarity(name1, name2)
    return sim if sim >= 0.9 else 0.0