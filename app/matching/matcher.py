"""Main patient matching API."""

from typing import List
from app.models.patient import Patient
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity
from app.matching.constants import PRECOMPUTED_NORMALIZATION_FIELDS
from app.matching.utils import log_elapsed_time

NO_MATCH = (None, -1, None)


def _normalized_fields_identical(patient1: Patient, patient2: Patient) -> bool:
    for _, norm_field in PRECOMPUTED_NORMALIZATION_FIELDS.items():
        norm1 = getattr(patient1, norm_field, "")
        norm2 = getattr(patient2, norm_field, "")
        if norm1 and norm2 and norm1 != norm2:
            return False
    return True


def _find_best_internal_match(external_patient, internal_patients):
    """Find the best matching internal patient for a given external patient based on normalized fields and similarity score."""
    candidates = [
        internal_patient
        for internal_patient in internal_patients
        if _normalized_fields_identical(external_patient, internal_patient)
    ]
    if not candidates:
        return NO_MATCH

    def score_tuple(internal_patient):
        score, breakdown = calculate_weighted_similarity(
            external_patient, internal_patient
        )
        return (internal_patient, score, breakdown)

    best_internal, best_score, best_breakdown = max(
        (score_tuple(internal_patient) for internal_patient in candidates),
        key=lambda x: x[1],
        default=NO_MATCH,
    )
    return best_internal, best_score, best_breakdown


@log_elapsed_time
def match_patients(internal: List[Patient], external: List[Patient]) -> List[dict]:
    """Match patients using weighted field similarity with early filtering. Only the best match per external patient is selected if above threshold."""
    matches = []

    for external_patient in external:
        best_internal, best_score, best_breakdown = _find_best_internal_match(
            external_patient, internal
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
