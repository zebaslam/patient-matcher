"""Main patient matching API."""
from typing import List, Dict, Any
from app.config import MATCH_THRESHOLD
from app.matching.scoring import calculate_weighted_similarity

def match_patients(internal: List[Dict[str, Any]], external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match patients using weighted field similarity."""
    matches = []

    for external_patient in external:
        for internal_patient in internal:
            similarity, breakdown = calculate_weighted_similarity(external_patient, internal_patient)
            if similarity >= MATCH_THRESHOLD:
                matches.append({
                    'external': external_patient,
                    'internal': internal_patient,
                    'score': similarity,
                    'breakdown': breakdown
                })

    return matches

