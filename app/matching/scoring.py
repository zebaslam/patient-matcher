"""Patient similarity scoring logic."""

from typing import Dict, Any, Tuple
from app.config import FIELD_WEIGHTS, FIELD_TYPES, PENALTIES
from app.matching.normalization import normalize_string
from app.matching.constants import (
    CRITICAL_FIELDS,
    PRECOMPUTED_NORMALIZATION_FIELDS,
    DEFAULT_PENALTY,
    DEFAULT_SIMILARITY,
)
from .field_similarity import calculate_field_similarity


def _get_normalized_precompute_values(patient1, patient2, field_name):
    """Return normalized values for a field, using precomputed if available."""
    precomputed_key = PRECOMPUTED_NORMALIZATION_FIELDS.get(field_name)
    if precomputed_key:
        n1 = patient1.get(precomputed_key, "")
        n2 = patient2.get(precomputed_key, "")
    else:
        raw1 = patient1.get(field_name)
        raw2 = patient2.get(field_name)
        n1 = normalize_string(str(raw1) if raw1 is not None else "", field_name)
        n2 = normalize_string(str(raw2) if raw2 is not None else "", field_name)
        normalized_key = precomputed_key or f"{field_name}Normalized"
        patient1[normalized_key] = n1
        patient2[normalized_key] = n2
    return n1, n2


def _update_breakdown_and_score(breakdown, field_name, sim, weight):
    wscore = sim * weight
    breakdown[field_name] = {
        "similarity": sim,
        "weight": weight,
        "weighted_score": wscore,
    }
    return wscore


def calculate_weighted_similarity(
    patient1: Dict[str, Any], patient2: Dict[str, Any]
) -> Tuple[float, dict]:
    """
    Calculate the weighted similarity score between two patient records.

    Args:
        patient1 (Dict[str, Any]): The first patient record.
        patient2 (Dict[str, Any]): The second patient record.

    Returns:
        Tuple[float, dict]: A tuple containing the final similarity score and a breakdown dictionary.
    """
    total_weighted_score = DEFAULT_SIMILARITY
    total_weight_used = DEFAULT_SIMILARITY
    breakdown = {}

    for field_name, weight in FIELD_WEIGHTS.items():
        n1, n2 = _get_normalized_precompute_values(patient1, patient2, field_name)
        if not n1 or not n2:
            continue

        sim = calculate_field_similarity(
            n1, n2, FIELD_TYPES.get(field_name, "general"), field_name
        )
        if field_name in CRITICAL_FIELDS and sim <= 0.05:
            return DEFAULT_SIMILARITY, {
                "early_exit": f"{field_name} too dissimilar",
                "fields": breakdown,
            }

        wscore = _update_breakdown_and_score(breakdown, field_name, sim, weight)
        total_weighted_score += wscore
        total_weight_used += weight

    final_score = total_weighted_score / total_weight_used if total_weight_used else 0.0
    final_score = max(DEFAULT_SIMILARITY, final_score - _calculate_penalty(breakdown))

    return final_score, {"fields": breakdown, "final_score": final_score}


def _calculate_penalty(breakdown: dict) -> float:
    penalty = DEFAULT_PENALTY

    # Example: apply penalty if similarity for a field is very low
    for field, field_penalty in PENALTIES.items():
        sim = breakdown.get(field, {}).get("similarity", 1.0)
        if sim < 0.5:  # or another threshold
            penalty += field_penalty

    return penalty
