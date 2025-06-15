"""
Data model representing a match score, including value, breakdown, threshold, and metadata.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass
class MatchScore:
    """
    Represents the similarity score between two entities, including an overall value,
    a breakdown of individual field scores (with weights and weighted scores), and optional metadata.

    Attributes:
        value (float): The overall similarity score between entities.
        breakdown (Dict[str, Dict[str, Any]]): A dictionary mapping field names to their individual similarity scores,
            weights, and weighted scores.
        threshold (Optional[float]): The threshold value used to determine if the match is significant.
        meets_threshold (bool): Indicates whether the score meets or exceeds the threshold.
        reason (Optional[str]): Additional explanation or notes about the match score.
    """

    value: float  # The overall similarity score
    breakdown: Dict[
        str, Dict[str, Any]
    ]  # Field-by-field breakdown: similarity, weight, weighted_score
    threshold: Optional[float] = None  # The threshold used for matching (if relevant)
    meets_threshold: bool = True
    reason: Optional[str] = None  # Optional explanation or notes
