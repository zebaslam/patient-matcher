"""Field-specific similarity functions for patient matching.

This module provides similarity calculations for different field types in patient records,
including names, phone numbers, addresses, and general text fields.
"""

from typing import Dict, Any, Callable

from app.config import (
    FIRST_NAME_MIDDLE_NAME,
    FIRST_NAME_MATCH,
    PHONE_PARTIAL_MATCH,
    GENERAL_SIMILARITY_MULTIPLIER,
)
from .string_similarity import similarity_ratio, token_overlap_score, jaro_winkler_similarity
from .normalization import _normalize_phone, normalize_string


class FieldSimilarityCalculator:
    """Centralized field similarity calculation with configurable handlers."""
    
    def __init__(self):
        self._field_handlers: Dict[str, Callable[[str, str], float]] = {
            "PhoneNumber": self._phone_similarity,
            "Address": self._address_similarity,
        }
        
        self._type_handlers: Dict[str, Callable[[str, str], float]] = {
            "exact": lambda n1, n2: 1.0 if n1 == n2 else 0.0,
            "name": self._name_similarity,
            "general": self._general_similarity,
        }

    def calculate(self, first_field: str, second_field: str, field_type: str, field_name: str) -> float:
        """Calculate similarity between two field values based on field type.
        
        Args:
            first_field: First field value to compare
            second_field: Second field value to compare
            field_type: Type category (exact, name, general)
            field_name: Specific field name (FirstName, PhoneNumber, etc.)
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Normalize inputs
            norm1 = normalize_string(first_field, field_name)
            norm2 = normalize_string(second_field, field_name)
            
            # Handle empty values
            if not norm1 or not norm2:
                return 0.0
                
            # Check for exact match first
            if norm1 == norm2:
                return 1.0
            
            # Use field-specific handler if available
            if field_name in self._field_handlers:
                return self._field_handlers[field_name](norm1, norm2)
            
            # Fall back to type-based handler
            handler = self._type_handlers.get(field_type, self._general_similarity)
            return handler(norm1, norm2)
            
        except Exception as e:
            print(f"Error calculating field similarity for {field_name}: {e}")
            return 0.0

    def _name_similarity(self, norm1: str, norm2: str) -> float:
        """Calculate similarity for name fields."""
        # This is a placeholder - actual implementation would use field_name context
        return self._first_name_similarity(norm1, norm2)

    def _first_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity for first names, handling middle names.
        
        Handles cases like:
        - "John" vs "John Michael" (first name + middle name)
        - "John Michael" vs "John David" (same first name, different middle)
        - Fuzzy matching with threshold
        """
        tokens1 = name1.lower().split()
        tokens2 = name2.lower().split()

        # Check for first name + middle name pattern
        first_middle_score = self._check_first_middle_pattern(tokens1, tokens2)
        if first_middle_score > 0:
            return first_middle_score

        # Check for same first name
        same_first_score = self._check_same_first_name(tokens1, tokens2)
        if same_first_score > 0:
            return same_first_score

        # Fallback to fuzzy matching
        return self._fuzzy_name_match(name1, name2)

    def _check_first_middle_pattern(self, tokens1: list, tokens2: list) -> float:
        """Check if one name is a subset of another (first name + middle name case)."""
        if len(tokens1) == len(tokens2):
            return 0.0
            
        shorter, longer = (tokens1, tokens2) if len(tokens1) < len(tokens2) else (tokens2, tokens1)
        if len(shorter) == 1 and len(longer) >= 1 and shorter[0] == longer[0]:
            return FIRST_NAME_MIDDLE_NAME
        
        return 0.0

    def _check_same_first_name(self, tokens1: list, tokens2: list) -> float:
        """Check if first names match exactly."""
        if tokens1 and tokens2 and tokens1[0] == tokens2[0]:
            return FIRST_NAME_MATCH
        return 0.0

    def _fuzzy_name_match(self, name1: str, name2: str) -> float:
        """Perform fuzzy matching with threshold for names."""
        similarity = jaro_winkler_similarity(name1, name2)
        return similarity if similarity >= FIRST_NAME_MATCH else 0.0

    def _last_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity for last names with high threshold."""
        similarity = jaro_winkler_similarity(name1, name2)
        return similarity if similarity >= 0.9 else 0.0

    def _general_similarity(self, norm1: str, norm2: str) -> float:
        """Calculate similarity for general text fields."""
        # Use token overlap for multi-word fields
        if ' ' in norm1 or ' ' in norm2:
            token_score = token_overlap_score(norm1, norm2)
            similarity_score = similarity_ratio(norm1, norm2) * GENERAL_SIMILARITY_MULTIPLIER
            return max(token_score, similarity_score)
        
        return similarity_ratio(norm1, norm2)

    def _phone_similarity(self, phone1: str, phone2: str) -> float:
        """Calculate similarity for phone numbers with partial matching."""
        norm1 = _normalize_phone(phone1)
        norm2 = _normalize_phone(phone2)

        if not norm1 or not norm2:
            return 0.0

        if norm1 == norm2:
            return 1.0

        # Check for suffix match (local number)
        if norm1.endswith(norm2) or norm2.endswith(norm1):
            return PHONE_PARTIAL_MATCH

        return 0.0

    def _address_similarity(self, addr1: str, addr2: str) -> float:
        """Calculate similarity for addresses with strict matching requirements."""
        if addr1 == addr2:
            return 1.0

        address1_parts = self._parse_address(addr1)
        address2_parts = self._parse_address(addr2)
        
        return self._score_address_match(address1_parts, address2_parts, addr1, addr2)

    def _parse_address(self, address: str) -> tuple[str, str]:
        """Extract street number and main street name from address."""
        tokens = address.split()
        street_number = tokens[0] if tokens and tokens[0].isdigit() else ""
        # Use first two tokens after number for main street name
        street_name = " ".join(tokens[1:3]).lower() if len(tokens) > 2 else " ".join(tokens[1:]).lower()
        return street_number, street_name

    def _score_address_match(self, parts1: tuple[str, str], parts2: tuple[str, str], 
                           full_addr1: str, full_addr2: str) -> float:
        """Score address similarity based on component matching."""
        street_num1, street_name1 = parts1
        street_num2, street_name2 = parts2

        # Exact match on both number and street name
        if street_num1 and street_num2 and street_num1 == street_num2 and street_name1 == street_name2:
            return 1.0
        # Same street name, different number
        elif street_name1 == street_name2:
            return 0.7
        # Same number, different street name
        elif street_num1 == street_num2:
            return 0.5

        # Fallback to token-based similarity with penalty
        token_score = token_overlap_score(full_addr1, full_addr2)
        similarity_score = similarity_ratio(full_addr1, full_addr2) * 0.5
        return max(token_score, similarity_score)


# Global calculator instance
_similarity_calculator = FieldSimilarityCalculator()


def calculate_field_similarity(first_field: str, second_field: str, field_type: str, field_name: str) -> float:
    """Public interface for field similarity calculation."""
    return _similarity_calculator.calculate(first_field, second_field, field_type, field_name)


def first_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity for first names."""
    return _similarity_calculator._first_name_similarity(name1, name2)


def last_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity for last names."""
    return _similarity_calculator._last_name_similarity(name1, name2)


def phone_similarity(phone1: str, phone2: str) -> float:
    """Calculate similarity for phone numbers."""
    return _similarity_calculator._phone_similarity(phone1, phone2)


def address_similarity(addr1: str, addr2: str) -> float:
    """Calculate similarity for addresses."""
    return _similarity_calculator._address_similarity(addr1, addr2)


def has_gender_mismatch(patient1: Dict[str, Any], patient2: Dict[str, Any]) -> bool:
    """Check if patients have conflicting gender information.
    
    Args:
        patient1: First patient record
        patient2: Second patient record
        
    Returns:
        True if both patients have gender info and they differ
    """
    sex1 = patient1.get('Sex')
    sex2 = patient2.get('Sex')
    return sex1 is not None and sex2 is not None and sex1 != sex2