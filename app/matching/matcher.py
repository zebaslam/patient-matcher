"""Main patient matching API."""
from typing import List, Dict, Any
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity
from app.matching.normalization import normalize_string
import time
import logging

def get_normalized(patient: Dict[str, Any], field: str) -> str:
    return normalize_string(patient.get(field, ""), field) if field == "DOB" else patient.get(field, "").strip().lower()

def match_patients(internal: List[Dict[str, Any]], external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match patients using weighted field similarity with early filtering."""
    matches = []
    start_time = time.time()

    # Precompute normalized fields ONCE
    for p in internal:
        p["_norm_dob"] = get_normalized(p, "DOB")
        p["_norm_gender"] = get_normalized(p, "Sex")

    for external_patient in external:
        ext_dob = get_normalized(external_patient, "DOB")
        ext_gender = get_normalized(external_patient, "Sex")

        for internal_patient in internal:
            int_dob = internal_patient["_norm_dob"]
            int_gender = internal_patient["_norm_gender"]

            # Early filter: skip if DOB or Gender are present in both and not equal
            if (ext_dob and int_dob and ext_dob != int_dob) or (ext_gender and int_gender and ext_gender != int_gender):
                continue

            similarity, breakdown = calculate_weighted_similarity(
                external_patient, internal_patient
            )
            if similarity >= MATCH_THRESHOLD:
                internal_clean = {k: v for k, v in internal_patient.items() if k not in {"_norm_dob", "_norm_gender"}}
                matches.append({
                    'external': external_patient,
                    'internal': internal_clean,
                    'score': similarity,
                    'breakdown': breakdown
                })
    elapsed = time.time() - start_time
    logging.info(f"Patient matching completed in {elapsed:.3f} seconds.")
    return matches

