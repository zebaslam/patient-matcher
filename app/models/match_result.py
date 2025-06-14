"""
Data model representing the result of a patient match.

Each MatchResult contains the external patient, the matched internal patient, the similarity score, and a breakdown of the score by field.
"""

from dataclasses import dataclass
from typing import Any, Dict

from app.models.patient import Patient
from app.models.best_match import BestMatch


@dataclass
class MatchResult:
    """
    Represents a single patient match result.

    Attributes:
        external: The external Patient being matched.
        internal: The matched internal Patient (must not be None).
        score: The similarity score for the match.
        breakdown: A dictionary with the breakdown of the score by field.
    """

    external: Patient
    internal: Patient  # type: ignore
    score: float
    breakdown: Dict[str, Any]

    @classmethod
    def from_best_match(cls, external: Patient, best_match: BestMatch) -> "MatchResult":
        """
        Creates a MatchResult instance from an external Patient and a BestMatch object.

        Args:
            external (Patient): The external patient to be matched.
            best_match (BestMatch): The best match result containing the internal patient and match details.

        Returns:
            MatchResult: A new MatchResult instance populated with the external patient, the matched internal patient, the match score, and the breakdown.

        Raises:
            ValueError: If best_match.internal is None.
        """
        if best_match.internal is None:
            raise ValueError(
                "BestMatch.internal cannot be None when creating a MatchResult."
            )
        return cls(
            external=external,
            internal=best_match.internal,
            score=best_match.score,
            breakdown=best_match.breakdown,
        )
