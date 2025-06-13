"""String similarity algorithms for patient matching.

This module provides various string similarity metrics commonly used in
record linkage and patient matching applications.
"""

from typing import Set, Tuple


class SimilarityMetrics:
    """Collection of string similarity algorithms for patient matching."""

    @staticmethod
    def _validate_strings(s1: str, s2: str) -> Tuple[str, str]:
        """Validate and normalize input strings."""
        if not isinstance(s1, str) or not isinstance(s2, str):
            raise TypeError("Both inputs must be strings")
        return s1.strip(), s2.strip()

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Split text into normalized tokens."""
        return set(text.lower().split())

    @classmethod
    def levenshtein_distance(cls, s1: str, s2: str) -> int:
        """Calculate minimum edit distance between two strings.

        Uses dynamic programming to find the minimum number of single-character
        edits (insertions, deletions, substitutions) required to transform s1 into s2.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Non-negative integer representing edit distance
        """
        s1, s2 = cls._validate_strings(s1, s2)

        if not s1:
            return len(s2)
        if not s2:
            return len(s1)

        # Ensure s1 is the shorter string for memory efficiency
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        # Use single row optimization
        previous_row = list(range(len(s2) + 1))

        for i, char1 in enumerate(s1):
            current_row = [i + 1]

            for j, char2 in enumerate(s2):
                insertion_cost = previous_row[j + 1] + 1
                deletion_cost = current_row[j] + 1
                substitution_cost = previous_row[j] + (char1 != char2)

                current_row.append(
                    min(insertion_cost, deletion_cost, substitution_cost)
                )

            previous_row = current_row

        return previous_row[-1]

    @classmethod
    def normalized_similarity(cls, s1: str, s2: str) -> float:
        """Calculate normalized similarity ratio based on edit distance.

        Returns a value between 0.0 (completely different) and 1.0 (identical).

        Args:
            s1: First string
            s2: Second string

        Returns:
            Float between 0.0 and 1.0 representing similarity ratio
        """
        s1, s2 = cls._validate_strings(s1, s2)

        max_length = max(len(s1), len(s2))
        if max_length == 0:
            return 1.0

        edit_distance = cls.levenshtein_distance(s1, s2)
        return 1.0 - (edit_distance / max_length)

    @classmethod
    def jaccard_similarity(cls, s1: str, s2: str) -> float:
        """Calculate Jaccard similarity coefficient for token sets.

        Measures overlap between two sets of tokens as |intersection| / |union|.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Float between 0.0 and 1.0 representing token overlap
        """
        s1, s2 = cls._validate_strings(s1, s2)

        tokens1 = cls._tokenize(s1)
        tokens2 = cls._tokenize(s2)

        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        return len(intersection) / len(union)

    @classmethod
    def _find_jaro_matches(cls, s1: str, s2: str) -> Tuple[int, int]:
        """Find character matches and transpositions for Jaro calculation.

        Returns:
            Tuple of (matches_count, transpositions_count)
        """
        len1, len2 = len(s1), len(s2)
        match_window = max(len1, len2) // 2 - 1
        match_window = max(0, match_window)
        matches, transpositions = 0, 0

        s1_matches, s2_matches, matches = cls._find_character_matches(
            s1, s2, match_window
        )

        if matches != 0:
            transpositions = cls._count_transpositions(s1, s2, s1_matches, s2_matches)
        return matches, transpositions

    @classmethod
    def _find_character_matches(
        cls, s1: str, s2: str, match_window: int
    ) -> Tuple[list, list, int]:
        """Find matching characters within the match window.

        Args:
            s1: First string
            s2: Second string
            match_window: Maximum distance for character matches

        Returns:
            Tuple of (s1_matches, s2_matches, total_matches)
        """
        len1, len2 = len(s1), len(s2)
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        matches = 0

        for i in range(len1):
            window_start = max(0, i - match_window)
            window_end = min(i + match_window + 1, len2)

            for j in range(window_start, window_end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue

                s1_matches[i] = s2_matches[j] = True
                matches += 1
                break

        return s1_matches, s2_matches, matches

    @classmethod
    def _count_transpositions(
        cls, s1: str, s2: str, s1_matches: list, s2_matches: list
    ) -> int:
        """Count character transpositions between matched characters.

        Args:
            s1: First string
            s2: Second string
            s1_matches: Boolean array indicating matches in s1
            s2_matches: Boolean array indicating matches in s2

        Returns:
            Number of transpositions
        """
        transpositions = 0
        k = 0

        for i, _ in enumerate(s1):
            if not s1_matches[i]:
                continue

            while not s2_matches[k]:
                k += 1

            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        return transpositions

    @classmethod
    def jaro_similarity(cls, s1: str, s2: str) -> float:
        """Calculate Jaro similarity between two strings.

        The Jaro similarity is based on the number of matching characters
        and transpositions, particularly effective for short strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Float between 0.0 and 1.0 representing Jaro similarity
        """
        s1, s2 = cls._validate_strings(s1, s2)

        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0

        matches, transpositions = cls._find_jaro_matches(s1, s2)

        if matches == 0:
            return 0.0

        jaro = (
            matches / len(s1)
            + matches / len(s2)
            + (matches - transpositions / 2) / matches
        ) / 3

        return jaro

    @classmethod
    def jaro_winkler_similarity(
        cls, s1: str, s2: str, prefix_weight: float = 0.1
    ) -> float:
        """Calculate Jaro-Winkler similarity with common prefix bonus.

        Enhances Jaro similarity by giving additional weight to strings
        that match from the beginning (common prefix).

        Args:
            s1: First string
            s2: Second string
            prefix_weight: Weight given to common prefix (default 0.1)

        Returns:
            Float between 0.0 and 1.0 representing Jaro-Winkler similarity
        """
        if not 0 <= prefix_weight <= 0.25:
            raise ValueError("prefix_weight must be between 0 and 0.25")

        s1, s2 = cls._validate_strings(s1, s2)
        jaro_score = cls.jaro_similarity(s1, s2)

        # Only apply prefix bonus if Jaro similarity is above threshold
        if jaro_score < 0.7:
            return jaro_score

        # Calculate common prefix length (maximum 4 characters)
        max_prefix_length = min(len(s1), len(s2), 4)
        common_prefix_length = 0

        for i in range(max_prefix_length):
            if s1[i] == s2[i]:
                common_prefix_length += 1
            else:
                break

        return jaro_score + (common_prefix_length * prefix_weight * (1 - jaro_score))

    @classmethod
    def combined_jaccard_levenshtein_similarity(
        cls, s1: str, s2: str, token_sim_threshold: float = 0.8
    ) -> float:
        """
        Combine Jaccard and Levenshtein similarity for robust address matching.

        Args:
            s1: First address string
            s2: Second address string
            token_sim_threshold: Minimum normalized similarity for tokens to be considered a match

        Returns:
            Float between 0.0 and 1.0 representing hybrid similarity
        """
        s1, s2 = cls._validate_strings(s1, s2)
        tokens1 = list(cls._tokenize(s1))
        tokens2 = list(cls._tokenize(s2))

        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        matched_indices = set()
        match_count = 0

        for t1 in tokens1:
            similarities = [
                (j, cls.normalized_similarity(t1, t2))
                for j, t2 in enumerate(tokens2)
                if j not in matched_indices
            ]
            if similarities:
                best_j, best_sim = max(similarities, key=lambda x: x[1])
                if best_sim >= token_sim_threshold:
                    match_count += 1
                    matched_indices.add(best_j)

        union = len(tokens1) + len(tokens2) - match_count
        return match_count / union if union > 0 else 1.0


def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate normalized similarity ratio between two strings using levenshtein distance."""
    return SimilarityMetrics.normalized_similarity(s1, s2)


def token_overlap_score(s1: str, s2: str) -> float:
    """Calculate Jaccard similarity for token overlap."""
    return SimilarityMetrics.jaccard_similarity(s1, s2)


def jaro_winkler_similarity(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
    """Calculate Jaro-Winkler similarity between two strings."""
    return SimilarityMetrics.jaro_winkler_similarity(s1, s2, prefix_scale)


def combined_jaccard_levenshtein_similarity(
    s1: str, s2: str, token_sim_threshold: float = 0.8
) -> float:
    """Hybrid Jaccard-Levenshtein similarity for address matching."""
    return SimilarityMetrics.combined_jaccard_levenshtein_similarity(
        s1, s2, token_sim_threshold
    )
