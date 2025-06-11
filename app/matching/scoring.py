"""Patient similarity scoring logic."""
from typing import Dict, Any, Tuple
from app.config import FIELD_WEIGHTS, FIELD_TYPES
from .field_similarity import calculate_field_similarity, has_gender_mismatch

def calculate_weighted_similarity(patient1: Dict[str, Any], patient2: Dict[str, Any]) -> Tuple[float, dict]:
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