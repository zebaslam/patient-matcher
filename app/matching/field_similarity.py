"""Field-specific similarity functions for patient matching.

This module provides similarity calculations for different field types in patient records,
including names, phone numbers, addresses, and general text fields.
"""

from app.config import (
    PHONE_PARTIAL_MATCH,
)
from app.models.field_similarity_result import FieldSimilarityResult
from .string_similarity import (
    levenshtein_similarity,
    jaccard_similarity,
    jaro_winkler_similarity,
    combined_jaccard_levenshtein_similarity,
)
from .normalization import _normalize_phone, normalize_string


def calculate_field_similarity(
    first_field, second_field, field_type, field_name
) -> FieldSimilarityResult:
    """
    Calculate similarity between two field values based on field type and name.
    Returns a FieldSimilarityResult.
    """
    norm1 = normalize_string(first_field, field_name)
    norm2 = normalize_string(second_field, field_name)

    if not norm1 or not norm2:
        return FieldSimilarityResult(0.0, "One more fields are empty")
    if norm1 == norm2:
        return FieldSimilarityResult(1.0, "exact")

    match (field_name, field_type):
        case (_, "exact"):
            return FieldSimilarityResult(1.0 if norm1 == norm2 else 0.0, "exact")
        case ("phone_number", _) | ("phone", _):
            sim = phone_similarity(norm1, norm2)
            return FieldSimilarityResult(sim, "levenshtein (phone)")
        case ("address", _):
            sim = combined_jaccard_levenshtein_similarity(norm1, norm2)
            return FieldSimilarityResult(sim, "combined_jaccard_levenshtein")
        case ("first_name", _):
            sim = first_name_similarity(norm1, norm2)
            return FieldSimilarityResult(sim, "jaro_winkler (first_name)")
        case ("last_name", _):
            sim = jaro_winkler_similarity(norm1, norm2)
            return FieldSimilarityResult(sim, "jaro_winkler (last_name)")
        case _:
            return general_similarity(norm1, norm2)


def first_name_similarity(name1, name2) -> float:
    """
    Compare first names using only the first token.
    """
    n1 = name1.split()[0] if name1 else ""
    n2 = name2.split()[0] if name2 else ""
    match (n1, n2):
        case ("", _) | (_, ""):
            return 0.0
        case _ if n1 == n2:
            return 1.0
        case _:
            return jaro_winkler_similarity(n1, n2)


def phone_similarity(phone1, phone2) -> float:
    """
    Compare phone numbers after normalization.
    """
    pn1 = _normalize_phone(phone1)
    pn2 = _normalize_phone(phone2)
    match (pn1, pn2):
        case (pn1, pn2) if pn1 == pn2 or (pn1 == "" and pn2 == ""):
            return 1.0
        case (pn1, pn2) if pn1 == "" or pn2 == "" or pn1 in pn2 or pn2 in pn1:
            return PHONE_PARTIAL_MATCH
        case _:
            sim = levenshtein_similarity(pn1, pn2)
            return sim if sim >= 0.5 else 0.0


def general_similarity(norm1, norm2) -> FieldSimilarityResult:
    """
    General similarity for normalized strings. Returns FieldSimilarityResult.
    """
    if " " in norm1 or " " in norm2:
        return FieldSimilarityResult(
            jaccard_similarity(norm1, norm2), "jaccard (general)"
        )
    return FieldSimilarityResult(
        levenshtein_similarity(norm1, norm2), "levenshtein (general)"
    )
