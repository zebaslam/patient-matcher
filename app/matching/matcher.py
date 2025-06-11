"""Main patient matching API."""

from typing import List
from models.patient import Patient
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity
from app.matching.constants import PRECOMPUTED_NORMALIZATION_FIELDS
from app.matching.utils import log_elapsed_time


def _normalized_fields_identical(patient1: Patient, patient2: Patient) -> bool:
    for _, norm_field in PRECOMPUTED_NORMALIZATION_FIELDS.items():
        norm1 = getattr(patient1, norm_field, "")
        norm2 = getattr(patient2, norm_field, "")
        if norm1 and norm2 and norm1 != norm2:
            return False
    return True


@log_elapsed_time
def match_patients(internal: List[Patient], external: List[Patient]) -> List[dict]:
    """Match patients using weighted field similarity with early filtering."""
    matches = []

    for p in internal:
        p.normalize_fields()

    for external_patient in external:
        external_patient.normalize_fields()

        for internal_patient in internal:
            if not _normalized_fields_identical(external_patient, internal_patient):
                continue

            similarity, breakdown = calculate_weighted_similarity(
                external_patient, internal_patient
            )
            if similarity >= MATCH_THRESHOLD:
                matches.append(
                    {
                        "external": external_patient,
                        "internal": internal_patient,
                        "score": similarity,
                        "breakdown": breakdown,
                    }
                )
    return matches
