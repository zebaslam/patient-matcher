"""Field-specific similarity functions for patient matching."""
import re
from typing import Dict, Any, Optional
from app.config import (
    FIRST_NAME_MIDDLE_NAME, FIRST_NAME_MATCH, ADDRESS_BASE_MATCH,
    PHONE_PARTIAL_MATCH, PHONE_AREA_CODE_MATCH, GENERAL_SIMILARITY_MULTIPLIER,
    ADDRESS_SIMILARITY_MULTIPLIER
)
from .similarity import similarity_ratio, token_overlap_score, jaro_winkler_similarity
from .utils import normalize_string, extract_base_address

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
        # Field-specific similarity functions (bypass normalization)
        field_handlers = {
            "PhoneNumber": phone_similarity,
            "Address": address_similarity,
        }
        
        if field_name in field_handlers:
            return field_handlers[field_name](first_field, second_field)
        
        # Standard flow with normalization
        norm1 = normalize_string(first_field, field_name)
        norm2 = normalize_string(second_field, field_name)
        
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
        return jaro_winkler_similarity(norm1, norm2)

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
    tokens1, tokens2 = name1.split(), name2.split()
    
    # Handle middle name scenarios
    if len(tokens1) != len(tokens2):
        shorter, longer = (tokens1, tokens2) if len(tokens1) < len(tokens2) else (tokens2, tokens1)
        
        # First name + middle name case
        if len(shorter) == 1 and len(longer) >= 1 and shorter[0] == longer[0]:
            return FIRST_NAME_MIDDLE_NAME
    
    # Same first name, different middle names
    if len(tokens1) >= 1 and len(tokens2) >= 1 and tokens1[0] == tokens2[0]:
        return FIRST_NAME_MATCH
    
    return jaro_winkler_similarity(name1, name2)

def phone_similarity(phone1: str, phone2: str) -> float:
    """Calculate similarity between phone numbers, handling partial matches."""
    norm1, norm2 = re.sub(r'\D', '', phone1), re.sub(r'\D', '', phone2)
    
    # Check basic similarity cases
    basic_result = _check_basic_similarity(norm1, norm2)
    if basic_result is not None:
        return basic_result
    
    # Check for suffix match (missing area code)
    if (len(norm1) >= 7 and len(norm2) >= 7 and 
        norm1[-7:] == norm2[-7:]):
        return PHONE_PARTIAL_MATCH
    
    # Check for area code only match
    if (len(norm1) >= 10 and len(norm2) >= 10 and 
        norm1[:3] == norm2[:3]):
        return PHONE_AREA_CODE_MATCH
    
    return similarity_ratio(norm1, norm2)

def address_similarity(addr1: str, addr2: str) -> float:
    """Calculate similarity between addresses, handling suite/apt variations."""
    # Check basic similarity cases
    basic_result = _check_basic_similarity(addr1, addr2)
    if basic_result is not None:
        return basic_result
    
    # Compare base addresses (without suite/apt)
    base1, base2 = extract_base_address(addr1), extract_base_address(addr2)
    
    if base1 == base2 and base1:
        return ADDRESS_BASE_MATCH
    
    # Fallback to token/similarity comparison
    token_score = token_overlap_score(addr1, addr2)
    similarity_score = similarity_ratio(addr1, addr2)
    
    return max(token_score, similarity_score * ADDRESS_SIMILARITY_MULTIPLIER)

def has_gender_mismatch(patient1: Dict[str, Any], patient2: Dict[str, Any]) -> bool:
    """Check if patients have different genders."""
    sex1, sex2 = patient1.get('Sex'), patient2.get('Sex')
    return sex1 is not None and sex2 is not None and sex1 != sex2