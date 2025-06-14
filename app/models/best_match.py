"""
Data model representing the result of finding the best internal match for a given external patient.

Contains the best internal patient, the similarity score, and the score breakdown.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from app.models.patient import Patient


@dataclass
class BestMatch:
    """
    Represents the best internal match for a given external patient.

    Attributes:
        internal: The best-matching internal Patient, or None if no match was found.
        score: The similarity score for the match (float, -1 if no match).
        breakdown: A dictionary with the breakdown of the score by field.
    """

    internal: Optional[Patient]
    score: float
    breakdown: Dict[str, Any]
