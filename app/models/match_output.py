"""
Data model representing a match output (for writing to CSV or API input).
"""

from dataclasses import dataclass


@dataclass
class MatchOutput:
    """
    Represents the output of a patient matching operation.

    Attributes:
        external_id (str): The identifier from the external system.
        internal_id (str): The identifier from the internal system.
    """

    external_id: str
    internal_id: str
