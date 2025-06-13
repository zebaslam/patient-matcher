"""Main patient matching API.

This module provides the main entry point for matching patients between two datasets.
It uses hash-based indexing for efficient pre-filtering and field-specific similarity scoring
for robust, configurable matching. The best match per external patient is returned if above threshold.
"""

from typing import List, Dict, Any
from collections import defaultdict
from app.models.patient import Patient
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity
from app.matching.constants import PRECOMPUTED_NORMALIZATION_FIELDS
from app.matching.utils import log_elapsed_time


NO_MATCH = (None, -1, None)


def _normalized_fields_identical(patient1: Patient, patient2: Patient) -> bool:
    """
    Check if all relevant normalized fields are identical between two patients.
    Used for filtering candidates based on strong identifiers (e.g., DOB, Sex).
    """
    for norm_field in PRECOMPUTED_NORMALIZATION_FIELDS.values():
        norm1 = getattr(patient1, norm_field, "")
        norm2 = getattr(patient2, norm_field, "")
        if norm1 and norm2 and norm1 != norm2:
            return False
    return True


def _find_best_internal_match(
    external_patient: Patient, internal_patients: List[Patient]
):
    """
    Find the best matching internal patient for a given external patient based on similarity score.
    Assumes all internal_patients already match on normalized fields (pre-filtered).
    Returns a tuple: (best_internal_patient, best_score, score_breakdown_dict),
    or NO_MATCH if no candidates are provided.
    """
    if not internal_patients:
        return NO_MATCH

    def score_tuple(internal_patient: Patient):
        score, breakdown = calculate_weighted_similarity(
            external_patient, internal_patient
        )
        return (internal_patient, score, breakdown)

    best_internal, best_score, best_breakdown = max(
        (score_tuple(internal_patient) for internal_patient in internal_patients),
        key=lambda x: x[1],
        default=NO_MATCH,
    )
    return best_internal, best_score, best_breakdown


@log_elapsed_time
def match_patients(
    internal: List[Patient], external: List[Patient]
) -> List[Dict[str, Any]]:
    """
    Match patients from two datasets using weighted field similarity with hash-based pre-filtering.
    - Internal patients are indexed by normalized fields (e.g., DOB, Sex) for fast candidate lookup.
    - For each external patient, only internal patients with matching normalized fields are considered.
    - The best match per external patient is selected if its score exceeds the configured threshold.
    - Returns a list of match dictionaries with external, internal, score, and breakdown keys.
    """
    matches = []
    if not internal or not external:
        return matches

    # Build an index of internal patients by their normalized fields for efficient lookup
    norm_fields = list(PRECOMPUTED_NORMALIZATION_FIELDS.values())
    index = defaultdict(list)
    for patient in internal:
        key = tuple(getattr(patient, norm_field, "") for norm_field in norm_fields)
        index[key].append(patient)

    for external_patient in external:
        key = tuple(
            getattr(external_patient, norm_field, "") for norm_field in norm_fields
        )
        candidates = index.get(key, [])
        best_internal, best_score, best_breakdown = _find_best_internal_match(
            external_patient, candidates
        )
        if best_score >= MATCH_THRESHOLD and best_internal is not None:
            matches.append(
                {
                    "external": external_patient,
                    "internal": best_internal,
                    "score": best_score,
                    "breakdown": best_breakdown,
                }
            )
    return matches
