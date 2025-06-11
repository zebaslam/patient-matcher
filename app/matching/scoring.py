"""Patient similarity scoring logic."""
from typing import Dict, Any, Tuple
from app.config import FIELD_WEIGHTS, FIELD_TYPES
from .field_similarity import calculate_field_similarity, has_gender_mismatch
from app.matching.normalization import normalize_string

def calculate_weighted_similarity(
    patient1: Dict[str, Any],
    patient2: Dict[str, Any]
) -> Tuple[float, dict]:
    critical_fields = {'DOB', 'FirstName', 'Address'}
    total_weighted_score = 0.0
    total_weight_used = 0.0
    breakdown = {}

    for field_name, weight in FIELD_WEIGHTS.items():
        # Use pre-normalized values for DOB and Gender if available
        if field_name == "DOB":
            n1 = patient1.get("DOBNormalized", "")
            n2 = patient2.get("DOBNormalized", "")
        else:
            raw1 = patient1.get(field_name)
            raw2 = patient2.get(field_name)
            n1 = normalize_string(str(raw1) if raw1 is not None else "", field_name)
            n2 = normalize_string(str(raw2) if raw2 is not None else "", field_name)
            # Store normalized values for UI display
            patient1[f"{field_name}Normalized"] = n1
            patient2[f"{field_name}Normalized"] = n2
        if not n1 or not n2:
            continue

        sim = calculate_field_similarity(n1, n2, FIELD_TYPES.get(field_name, "general"), field_name)
        if field_name in critical_fields and sim <= 0.05:
            return 0.0, {"early_exit": f"{field_name} too dissimilar", "fields": breakdown}

        wscore = sim * weight
        breakdown[field_name] = {"similarity": sim, "weight": weight, "weighted_score": wscore}
        total_weighted_score += wscore
        total_weight_used += weight

    final_score = total_weighted_score / total_weight_used if total_weight_used else 0.0
    final_score = max(0.0, final_score - _calculate_penalty(breakdown, patient1, patient2))

    return final_score, {"fields": breakdown, "final_score": final_score}

def _calculate_penalty(breakdown: dict, patient1: Dict[str, Any], patient2: Dict[str, Any]) -> float:
    penalty = 0.4 if has_gender_mismatch(patient1, patient2) else 0.0
    phone_sim = breakdown.get('PhoneNumber', {}).get('similarity', 1.0)
    strong_fields = [
        breakdown.get('FirstName', {}).get('similarity', 1.0),
        breakdown.get('DOB', {}).get('similarity', 1.0),
        breakdown.get('Address', {}).get('similarity', 1.0),
    ]
    if phone_sim < 0.5 and sum(1 for s in strong_fields if s > 0.9) < 3:
        penalty += 0.1
    return penalty