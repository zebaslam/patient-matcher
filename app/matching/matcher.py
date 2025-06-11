"""Main patient matching API."""
from typing import List, Dict, Any
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity
from app.matching.normalization import normalize_string
import time
import logging

def __get_normalized(patient: Dict[str, Any], field: str) -> str:
    return normalize_string(patient.get(field, ""), field)

def __normalize_patient_fields(patient: Dict[str, Any], fields: List[str]) -> None:
    for field in fields:
        patient[f"{field}Normalized"] = __get_normalized(patient, field)
        
def __normalized_fields_identical(
    patient1: Dict[str, Any], patient2: Dict[str, Any],
) -> bool:
    """Compare normalized fields of two patients."""
    for field in ["DOB", "Sex"]:
        norm1 = patient1.get(f"{field}Normalized", "")
        norm2 = patient2.get(f"{field}Normalized", "")
        if norm1 and norm2 and norm1 != norm2:
            return False
    return True

def match_patients(internal: List[Dict[str, Any]], external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match patients using weighted field similarity with early filtering."""
    matches = []
    start_time = time.time()
    norm_fields = ["DOB", "Sex"]

    # Precompute normalized fields ONCE
    for p in internal:
        __normalize_patient_fields(p, norm_fields)

    for external_patient in external:
        __normalize_patient_fields(external_patient, norm_fields)

        for internal_patient in internal:

            # Early filter: skip if DOB or Gender are present in both and not equal
            if not __normalized_fields_identical(external_patient, internal_patient):
                continue

            similarity, breakdown = calculate_weighted_similarity(
                external_patient, internal_patient
            )
            if similarity >= MATCH_THRESHOLD:
                internal_clean = {k: v for k, v in internal_patient.items()}
                matches.append({
                    'external': external_patient,
                    'internal': internal_clean,
                    'score': similarity,
                    'breakdown': breakdown
                })
    elapsed = time.time() - start_time
    logging.info(f"Patient matching completed in {elapsed:.3f} seconds.")
    return matches

