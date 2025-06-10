"""Main patient matching API."""
import csv
import re
from typing import List, Dict, Any
from app.config import MATCHES_CSV_PATH, FIELD_WEIGHTS, FIELD_TYPES, MATCH_THRESHOLD, ENCODING
from .similarity import similarity_ratio, token_overlap_score, jaro_winkler_similarity
from .utils import normalize_string, extract_base_address

def _calculate_field_similarity(first_field: str, second_field: str, field_type: str, field_name: str) -> float:
    """Calculate similarity between two field values based on field type."""
    try:
        norm1 = normalize_string(first_field, field_name)
        norm2 = normalize_string(second_field, field_name)
        
        if not norm1 or not norm2:
            return 0.0
        if norm1 == norm2:
            return 1.0
        
        if field_type == "exact":
            return 0.0
        elif field_type == "name":
            result = jaro_winkler_similarity(norm1, norm2)
        elif field_name == "PhoneNumber":  # Special handling for phones
            result = _phone_similarity(norm1, norm2)
        elif field_name == "Address":  # Special handling for addresses
            result = _address_similarity(norm1, norm2)
        else:  # "general"
            if ' ' in norm1 or ' ' in norm2:
                token_score = token_overlap_score(norm1, norm2)
                similarity_score = similarity_ratio(norm1, norm2)
                result = max(token_score, similarity_score * 0.7)
            else:
                result = similarity_ratio(norm1, norm2)
        
        # Ensure we always return a float
        if result is None:
            print(f"Warning: similarity function returned None for '{norm1}' vs '{norm2}' (type: {field_type})")
            return 0.0
            
        return float(result)
        
    except Exception as e:
        print(f"Error calculating field similarity: {e}")
        return 0.0

def _calculate_weighted_similarity(patient1: Dict[str, Any], patient2: Dict[str, Any]) -> float:
    """Calculate weighted similarity score between two patients."""
    total_weighted_score = 0.0
    total_weight_used = 0.0
    
    for field_name, weight in FIELD_WEIGHTS.items():
        if field_name in patient1 and field_name in patient2:
            field_type = FIELD_TYPES.get(field_name, "general")
            
            similarity = _calculate_field_similarity(
                patient1[field_name], patient2[field_name], field_type, field_name
            )
            
            # Debug check
            if similarity is None:
                print(f"Warning: field similarity is None for field {field_name}")
                similarity = 0.0
            
            total_weighted_score += similarity * weight
            total_weight_used += weight
    
    return total_weighted_score / total_weight_used if total_weight_used > 0 else 0.0

def match_patients(internal: List[Dict[str, Any]], external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match patients using weighted field similarity."""
    matches = []
    
    for external_patient in external:
        for internal_patient in internal:
            similarity = _calculate_weighted_similarity(external_patient, internal_patient)
            if similarity >= MATCH_THRESHOLD:
                matches.append({
                    'external': external_patient,
                    'internal': internal_patient,
                    'score': similarity
                })
    
    return matches

def write_match(external_id: str, internal_id: str) -> bool:
    """Write a match to the matches CSV file."""
    try:
        with open(MATCHES_CSV_PATH, 'a', newline='', encoding=ENCODING) as f:
            writer = csv.writer(f)
            writer.writerow([external_id, internal_id])
        return True
    except Exception as e:
        print(f"Error writing match: {e}")
        return False

def _phone_similarity(phone1: str, phone2: str) -> float:
    """Calculate similarity between phone numbers, handling partial matches."""
    # Normalize both phones
    norm1 = re.sub(r'\D', '', phone1)  # digits only
    norm2 = re.sub(r'\D', '', phone2)  # digits only
    
    if not norm1 or not norm2:
        return 0.0
    
    # Exact match
    if norm1 == norm2:
        return 1.0
    
    # Check if one is a suffix of the other (area code missing)
    if len(norm1) >= 7 and len(norm2) >= 7:
        last7_1 = norm1[-7:]
        last7_2 = norm2[-7:]
        if last7_1 == last7_2:
            return 0.9  # High similarity for matching local numbers
    
    # Fallback to general string similarity
    return similarity_ratio(norm1, norm2)

def _address_similarity(addr1: str, addr2: str) -> float:
    """Calculate similarity between addresses, handling suite/apt variations."""
    if not addr1 or not addr2:
        return 0.0
    
    if addr1 == addr2:
        return 1.0
    
    # Extract base address (without suite/apt)
    base1 = extract_base_address(addr1)
    base2 = extract_base_address(addr2)
    
    # If base addresses match exactly, high similarity
    if base1 == base2 and base1:
        return 0.95
    
    # Use token overlap for partial matches
    token_score = token_overlap_score(addr1, addr2)
    similarity_score = similarity_ratio(addr1, addr2)
    
    return max(token_score, similarity_score * 0.8)
