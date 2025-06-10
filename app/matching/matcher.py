"""Main patient matching API."""
import csv
from typing import List, Dict, Any
from app.config import MATCHES_CSV_PATH, FIELD_WEIGHTS, FIELD_TYPES, MATCH_THRESHOLD, ENCODING
from .similarity import similarity_ratio, token_overlap_score, jaro_winkler_similarity
from .utils import normalize_string, get_patient_id
from .data_loader import load_data

def _calculate_field_similarity(first_field: str, second_field: str, field_type: str) -> float:
    """Calculate similarity between two field values based on field type."""
    try:
        norm1 = normalize_string(first_field)
        norm2 = normalize_string(second_field)
        
        if not norm1 or not norm2:
            return 0.0
        if norm1 == norm2:
            return 1.0
        
        if field_type == "exact":
            return 0.0
        elif field_type == "name":
            result = jaro_winkler_similarity(norm1, norm2)
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
                patient1[field_name], patient2[field_name], field_type
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