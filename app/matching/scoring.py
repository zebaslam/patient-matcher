"""Patient similarity scoring logic.

This module provides functions to calculate the weighted similarity score between two patient records.
It uses configurable field weights and types, and supports penalizing missing data for critical fields.
"""

from typing import Tuple
from app.models.patient import Patient
from app.config import FIELD_WEIGHTS, FIELD_TYPES
from app.matching.constants import (
    CRITICAL_FIELDS,
    NORMALIZED_FIELDS,
    DEFAULT_SIMILARITY,
)
from .field_similarity import calculate_field_similarity


def _get_normalized_precompute_values(
    patient1: Patient, patient2: Patient, field_name: str
):
    """
    Return normalized values for a field, using normalized attributes if available.

    Args:
        patient1 (Patient): The first patient object.
        patient2 (Patient): The second patient object.
        field_name (str): The name of the field to normalize.

    Returns:
        Tuple[str, str]: The normalized values for the field from both patients.
    """
    norm_field = NORMALIZED_FIELDS.get(field_name, f"{field_name}_norm")
    n1 = getattr(patient1, norm_field, "")
    n2 = getattr(patient2, norm_field, "")
    return n1, n2


def _update_breakdown_and_score(breakdown, field_name, sim, weight):
    """
    Update the breakdown dictionary and calculate the weighted score for a field.

    Args:
        breakdown (dict): The breakdown dictionary to update.
        field_name (str): The name of the field.
        sim (float): The similarity score for the field.
        weight (float): The weight assigned to the field.

    Returns:
        float: The weighted score for the field.
    """
    wscore = sim * weight
    breakdown[field_name] = {
        "similarity": sim,
        "weight": weight,
        "weighted_score": wscore,
    }
    return wscore


def calculate_weighted_similarity(
    patient1: Patient, patient2: Patient
) -> Tuple[float, dict]:
    """
    Calculate the weighted similarity score between two patient records.

    This function computes a similarity score based on field weights and types,
    penalizing missing data for critical fields, and returns a breakdown of the
    similarity calculation.

    Args:
        patient1 (Patient): The first patient object.
        patient2 (Patient): The second patient object.

    Returns:
        Tuple[float, dict]: The final similarity score and a breakdown dictionary.
    """
    # Ensure all normalized fields are present
    patient1.normalize_fields()
    patient2.normalize_fields()

    total_weighted_score = DEFAULT_SIMILARITY
    total_weight_used = DEFAULT_SIMILARITY
    breakdown = {}

    for field_name, weight in FIELD_WEIGHTS.items():
        n1, n2 = _get_normalized_precompute_values(patient1, patient2, field_name)
        # Penalize missing data for critical fields
        if (not n1 or not n2) and field_name in CRITICAL_FIELDS:
            sim = 0.0
        elif not n1 or not n2:
            sim = 0.5
        else:
            sim = calculate_field_similarity(
                n1, n2, FIELD_TYPES.get(field_name, "general"), field_name
            )

        wscore = _update_breakdown_and_score(breakdown, field_name, sim, weight)
        total_weighted_score += wscore
        total_weight_used += weight

    final_score = total_weighted_score / total_weight_used if total_weight_used else 0.0
    final_score = max(DEFAULT_SIMILARITY, final_score)

    return final_score, {"fields": breakdown, "final_score": final_score}
