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
        val1 = patient1.get(field_name)
        val2 = patient2.get(field_name)
        if val1 is not None and val2 is not None:
            field_type = FIELD_TYPES.get(field_name, "general")
            if val1 and val2:
                similarity = calculate_field_similarity(val1, val2, field_type, field_name)
            else:
                similarity = 0.5  # Neutral score for missing value
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

    # Apply additional penalties
    penalty = _calculate_penalty(breakdown)
    final_score = max(0.0, final_score - penalty)

    return final_score, {
        "fields": breakdown,
        "gender_penalty_applied": gender_penalty_applied,
        "final_score": final_score
    }

def _calculate_penalty(breakdown: dict) -> float:
    """Calculate penalty based on critical field similarities."""
    penalty = 0.0

    phone_sim = breakdown.get('PhoneNumber', {}).get('similarity', 1.0)
    strong_fields = [
        breakdown.get('FirstName', {}).get('similarity', 1.0),
        breakdown.get('DOB', {}).get('similarity', 1.0),
        breakdown.get('Address', {}).get('similarity', 1.0),
    ]
    strong_count = sum(1 for s in strong_fields if s > 0.9)

    # Only penalize phone if not enough strong fields
    if phone_sim < 0.5 and strong_count < 3:
        penalty += 0.1

    return penalty

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
