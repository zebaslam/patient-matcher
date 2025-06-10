"""Main patient matching API."""
import csv
from typing import List, Dict, Any
from app.config import MATCHES_CSV_PATH, FIELD_WEIGHTS, FIELD_TYPES, MATCH_THRESHOLD, ENCODING
from .field_similarity import calculate_field_similarity, has_gender_mismatch

def match_patients(internal: List[Dict[str, Any]], external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match patients using weighted field similarity."""
    matches = []

    for external_patient in external:
        for internal_patient in internal:
            similarity, breakdown = calculate_weighted_similarity(external_patient, internal_patient)
            if similarity >= MATCH_THRESHOLD:
                matches.append({
                    'external': external_patient,
                    'internal': internal_patient,
                    'score': similarity,
                    'breakdown': breakdown
                })

    return matches

def calculate_weighted_similarity(patient1: Dict[str, Any], patient2: Dict[str, Any]) -> tuple[float, dict]:
    """Calculate weighted similarity score and breakdown between two patients."""
    total_weighted_score = 0.0
    total_weight_used = 0.0
    breakdown = {}

    for field_name, weight in FIELD_WEIGHTS.items():
        if field_name in patient1 and field_name in patient2:
            field_type = FIELD_TYPES.get(field_name, "general")
            similarity = calculate_field_similarity(
                patient1[field_name], patient2[field_name], field_type, field_name
            )
            weighted_score = similarity * weight
            breakdown[field_name] = {
                "similarity": similarity,
                "weight": weight,
                "weighted_score": weighted_score
            }
            total_weighted_score += weighted_score
            total_weight_used += weight

    final_score = total_weighted_score / total_weight_used if total_weight_used > 0 else 0.0

    # Apply gender mismatch penalty
    gender_penalty_applied = False
    if has_gender_mismatch(patient1, patient2):
        final_score *= 0.6  # 40% penalty for gender mismatch
        gender_penalty_applied = True

    return final_score, {
        "fields": breakdown,
        "gender_penalty_applied": gender_penalty_applied,
        "final_score": final_score
    }

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
