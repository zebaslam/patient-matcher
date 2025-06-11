"""Main patient matching API."""

from typing import List, Dict, Any
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity
from app.matching.normalization import normalize_string
from app.matching.constants import PRECOMPUTED_NORMALIZATION_FIELDS
from app.matching.utils import log_elapsed_time


def _get_normalized(patient: Dict[str, Any], field: str) -> str:
    return normalize_string(patient.get(field, ""), field)


def _normalize_patient_fields(patient: Dict[str, Any]) -> None:
    """
    Adds normalized fields to the patient dict in place.
    Assumes patient dicts are not reused elsewhere after normalization.
    """
    for field, norm_field in PRECOMPUTED_NORMALIZATION_FIELDS.items():
        patient[norm_field] = _get_normalized(patient, field)


def _normalized_fields_identical(
    patient1: Dict[str, Any],
    patient2: Dict[str, Any],
) -> bool:
    for _, norm_field in PRECOMPUTED_NORMALIZATION_FIELDS.items():
        norm1 = patient1.get(norm_field, "")
        norm2 = patient2.get(norm_field, "")
        if norm1 and norm2 and norm1 != norm2:
            return False
    return True


@log_elapsed_time
def match_patients(
    internal: List[Dict[str, Any]], external: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Match patients using weighted field similarity with early filtering."""
    matches = []

    # Precompute normalized fields ONCE
    for p in internal:
        _normalize_patient_fields(p)

    for external_patient in external:
        _normalize_patient_fields(external_patient)

        for internal_patient in internal:

            # Early filter: skip if DOB or Gender are present in both and not equal
            if not _normalized_fields_identical(external_patient, internal_patient):
                continue

            similarity, breakdown = calculate_weighted_similarity(
                external_patient, internal_patient
            )
            if similarity >= MATCH_THRESHOLD:
                internal_clean = {k: v for k, v in internal_patient.items()}
                matches.append(
                    {
                        "external": external_patient,
                        "internal": internal_clean,
                        "score": similarity,
                        "breakdown": breakdown,
                    }
                )
    return matches
