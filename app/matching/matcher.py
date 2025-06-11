"""Main patient matching API."""
from typing import List, Dict, Any
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity
from app.matching.normalization import normalize_string
import time
import logging

def get_normalized(patient: Dict[str, Any], field: str) -> str:
    return normalize_string(patient.get(field, ""), field)

def match_patients(internal: List[Dict[str, Any]], external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match patients using weighted field similarity with early filtering."""
    matches = []
    start_time = time.time()

    # Precompute normalized fields ONCE using the Normalized suffix
    for p in internal:
        p["DOBNormalized"] = get_normalized(p, "DOB")
        p["SexNormalized"] = get_normalized(p, "Sex")

    for external_patient in external:
        external_patient["DOBNormalized"] = get_normalized(external_patient, "DOB")
        external_patient["SexNormalized"] = get_normalized(external_patient, "Sex")

        ext_dob = external_patient["DOBNormalized"]
        ext_gender = external_patient["SexNormalized"]

        for internal_patient in internal:
            int_dob = internal_patient["DOBNormalized"]
            int_gender = internal_patient["SexNormalized"]

            # Early filter: skip if DOB or Gender are present in both and not equal
            if (ext_dob and int_dob and ext_dob != int_dob) or (ext_gender and int_gender and ext_gender != int_gender):
                continue

            similarity, breakdown = calculate_weighted_similarity(
                external_patient, internal_patient
            )
            if similarity >= MATCH_THRESHOLD:
                # Remove only the Normalized fields you don't want to show, if any
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

