"""
Data model representing the result of finding the best internal match for a given external patient.

Contains the best internal patient and the similarity score.
"""

from dataclasses import dataclass
from typing import Optional
from app.models.patient import Patient
from app.models.match_score import MatchScore


@dataclass
class BestMatch:
    """
    Represents the best internal match for a given external patient.

    Attributes:
        internal: The best-matching internal Patient, or None if no match was found.
        score: The similarity score for the match (MatchScore, -1 if no match).
    """

    internal: Optional[Patient]
    score: MatchScore
