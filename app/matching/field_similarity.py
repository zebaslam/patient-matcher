"""Field-specific similarity functions for patient matching.

This module provides similarity calculations for different field types in patient records,
including names, phone numbers, addresses, and general text fields.
"""

from app.config import (
    FIRST_NAME_MIDDLE_NAME,
    FIRST_NAME_MATCH,
    PHONE_PARTIAL_MATCH,
    GENERAL_SIMILARITY_MULTIPLIER,
)
from .string_similarity import (
    similarity_ratio,
    token_overlap_score,
    jaro_winkler_similarity,
)
from .normalization import _normalize_phone, normalize_string


def calculate_field_similarity(first_field, second_field, field_type, field_name):
    """
    Calculate similarity between two field values based on field type and name.

    Args:
        first_field (str): The first field value to compare.
        second_field (str): The second field value to compare.
        field_type (str): The type of the field (e.g., 'name', 'exact').
        field_name (str): The name of the field (e.g., 'first_name', 'phone_number').

    Returns:
        float: Similarity score between 0.0 and 1.0.
    """
    norm1 = normalize_string(first_field, field_name)
    norm2 = normalize_string(second_field, field_name)
    if not norm1 or not norm2:
        return 0.0
    if norm1 == norm2:
        return 1.0

    match (field_name, field_type):
        case ("phone_number", _) | ("phone", _):
            return phone_similarity(norm1, norm2)
        case ("address", _):
            return address_similarity(norm1, norm2)
        case ("first_name", "name"):
            return first_name_similarity(norm1, norm2)
        case ("last_name", "name"):
            return last_name_similarity(norm1, norm2)
        case (_, "exact"):
            return 1.0 if norm1 == norm2 else 0.0
        case _:
            return general_similarity(norm1, norm2)


def first_name_similarity(name1, name2):
    """
    Compute similarity between two first names, accounting for typos and middle names.
    """
    n1 = name1.strip().lower()
    n2 = name2.strip().lower()
    if n1 == n2:
        return 1.0

    t1 = n1.split()
    t2 = n2.split()

    # Single-token vs multi-token (middle name) cases
    if (len(t1) == 1 and len(t2) > 1 and t1[0] == t2[0]) or (
        len(t2) == 1 and len(t1) > 1 and t2[0] == t1[0]
    ):
        return FIRST_NAME_MIDDLE_NAME

    # Prefix match (first token matches)
    if t1 and t2 and t1[0] == t2[0]:
        return FIRST_NAME_MATCH

    # Always fallback to Jaro-Winkler for typo tolerance
    sim = jaro_winkler_similarity(n1, n2)
    return sim if sim >= FIRST_NAME_MATCH else 0.0


def last_name_similarity(name1, name2):
    """
    Compute similarity between two last names using Jaro-Winkler similarity.

    Args:
        name1 (str): The first last name.
        name2 (str): The second last name.

    Returns:
        float: Similarity score between 0.0 and 1.0.
    """
    # similarity = jaro_winkler_similarity(name1, name2)
    return jaro_winkler_similarity(name1, name2)


def phone_similarity(phone1, phone2):
    """
    Compute similarity between two phone numbers.

    Args:
        phone1 (str): The first phone number.
        phone2 (str): The second phone number.

    Returns:
        float: Similarity score between 0.0 and 1.0.
    """

    match (_normalize_phone(phone1), _normalize_phone(phone2)):
        case (pn1, pn2) if pn1 == pn2 or (pn1 == "" and pn2 == ""):
            return 1.0
        case (pn1, pn2) if pn1 == "" or pn2 == "" or pn1 in pn2 or pn2 in pn1:
            return PHONE_PARTIAL_MATCH
        case _:
            sim = similarity_ratio(pn1, pn2)
            return sim if sim >= 0.5 else 0.0


def address_similarity(addr1, addr2):
    """
    Compute similarity between two addresses.

    Args:
        addr1 (str): The first address.
        addr2 (str): The second address.

    Returns:
        float: Similarity score between 0.0 and 1.0.
    """
    if addr1 == addr2:
        return 1.0
    num1, street1 = parse_address(addr1)
    num2, street2 = parse_address(addr2)
    if num1 and num2 and num1 == num2 and street1 == street2:
        return 1.0
    elif street1 == street2:
        return 0.7
    elif num1 == num2:
        return 0.5
    # Fix: If both street and number do not match, return 0.0
    return 0.0


def parse_address(address):
    """
    Parse an address string into street number and street name components.

    Args:
        address (str): The address string.

    Returns:
        tuple: (street_number (str), street_name (str))
    """
    tokens = address.split()
    street_number = tokens[0] if tokens and tokens[0].isdigit() else ""
    street_name = (
        " ".join(tokens[1:3]).lower()
        if len(tokens) > 2
        else " ".join(tokens[1:]).lower()
    )
    return street_number, street_name


def general_similarity(norm1, norm2):
    """
    Compute general similarity between two normalized strings.

    Args:
        norm1 (str): The first normalized string.
        norm2 (str): The second normalized string.

    Returns:
        float: Similarity score between 0.0 and 1.0.
    """
    if " " in norm1 or " " in norm2:
        token_score = token_overlap_score(norm1, norm2)
        similarity_score = (
            similarity_ratio(norm1, norm2) * GENERAL_SIMILARITY_MULTIPLIER
        )
        return max(token_score, similarity_score)
    return similarity_ratio(norm1, norm2)
