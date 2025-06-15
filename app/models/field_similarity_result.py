from dataclasses import dataclass


@dataclass
class FieldSimilarityResult:
    """
    Represents the result of a similarity comparison between two fields.

    Attributes:
        similarity (float): The computed similarity score between the fields.
        algorithm (str): The name of the algorithm used to compute the similarity.
    """

    similarity: float
    algorithm: str
