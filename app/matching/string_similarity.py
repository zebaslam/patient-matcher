"""String similarity algorithms for patient matching and record linkage."""

from typing import Set, Tuple
from .constants import JARO_THRESHOLD


def validate_strings(s1: str, s2: str) -> Tuple[str, str]:
    """Ensure both inputs are strings and strip leading and trailing whitespace."""
    if not isinstance(s1, str) or not isinstance(s2, str):
        raise TypeError("Both inputs must be strings")
    return s1.strip(), s2.strip()


class SimilarityMetrics:
    """String similarity algorithms for patient matching."""

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Tokenize text into a set of lowercase words."""
        return set(text.lower().split())

    @staticmethod
    def levenshtein_distance(a: str, b: str) -> int:
        """Compute Levenshtein edit distance between two strings."""
        if not a:
            return len(b)
        if not b:
            return len(a)
        if len(a) > len(b):
            a, b = b, a
        prev_row = list(range(len(b) + 1))
        for i, ca in enumerate(a):
            curr_row = [i + 1]
            for j, cb in enumerate(b):
                substitution_cost = 1 if ca != cb else 0
                insert = prev_row[j + 1] + 1
                delete = curr_row[j] + 1
                subst = prev_row[j] + substitution_cost
                curr_row.append(min(insert, delete, subst))
            prev_row = curr_row
        return prev_row[-1]

    @classmethod
    def normalized_levenshtein_similarity(cls, s1: str, s2: str) -> float:
        """Normalized Levenshtein similarity (0.0–1.0)."""
        s1, s2 = validate_strings(s1, s2)
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        dist = cls.levenshtein_distance(s1, s2)
        return 1.0 - (dist / max_len)

    @classmethod
    def jaccard_similarity(cls, s1: str, s2: str) -> float:
        """Jaccard similarity for token sets (0.0–1.0)."""
        s1, s2 = validate_strings(s1, s2)
        tokens1, tokens2 = cls._tokenize(s1), cls._tokenize(s2)
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        return len(intersection) / len(union)

    @classmethod
    def compute_jaro_similarity(cls, s1: str, s2: str) -> float:
        """
        Jaro similarity (0.0–1.0), effective for short strings.

        The formula for Jaro similarity is:
        J = (1/3) * (m/|s1| + m/|s2| + (m - t)/m),
        where:
        - m is the number of matching characters,
        - t is the number of transpositions,
        - |s1| and |s2| are the lengths of the strings s1 and s2.
        """
        s1, s2 = validate_strings(s1, s2)
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0

        matches, transpositions = cls._find_jaro_matches(s1, s2)
        if matches == 0:
            return 0.0
        match_ratio_s1 = matches / len(s1)
        match_ratio_s2 = matches / len(s2)
        transposition_ratio = (matches - (transpositions / 2)) / matches
        return (match_ratio_s1 + match_ratio_s2 + transposition_ratio) / 3

    @classmethod
    def _find_jaro_matches(cls, s1: str, s2: str) -> Tuple[int, int]:
        """Find matches and transpositions for Jaro similarity."""
        s1, s2 = validate_strings(s1, s2)
        len1, len2 = len(s1), len(s2)
        window = max(len1, len2) // 2 - 1 if len1 > 0 and len2 > 0 else 0
        if len1 == 0 or len2 == 0:
            window = 0
        s1_matches, s2_matches, matches = cls._find_character_matches(s1, s2, window)
        transpositions = (
            cls._count_transpositions(s1, s2, s1_matches, s2_matches) if matches else 0
        )
        return matches, transpositions

    @classmethod
    def _find_character_matches(
        cls, s1: str, s2: str, window: int
    ) -> Tuple[list, list, int]:
        """Find matching characters within a window for Jaro."""
        len1, len2 = len(s1), len(s2)
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        matches = 0
        for i in range(len1):
            start = max(0, i - window)
            end = min(i + window + 1, len2)
            for j in range(start, end):
                if not s2_matches[j] and s1[i] == s2[j]:
                    s1_matches[i] = s2_matches[j] = True
                    matches += 1
                    break
        return s1_matches, s2_matches, matches

    @classmethod
    def _count_transpositions(
        cls, s1: str, s2: str, s1_matches: list, s2_matches: list
    ) -> int:
        """Count transpositions for Jaro similarity."""
        transpositions = 0
        k = 0
        for i, matched in enumerate(s1_matches):
            if not matched:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        return transpositions

    @classmethod
    def jaro_winkler_similarity(
        cls, s1: str, s2: str, prefix_weight: float = 0.1
    ) -> float:
        """Jaro-Winkler similarity (0.0–1.0) with prefix bonus."""
        s1, s2 = validate_strings(s1, s2)
        jaro = cls.compute_jaro_similarity(s1, s2)
        if jaro < JARO_THRESHOLD:
            return jaro
        prefix_len = 0
        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i] and prefix_len < 4:
                prefix_len += 1
            else:
                break
        return jaro + (prefix_len * prefix_weight * (1 - jaro))

    @classmethod
    def combined_jaccard_levenshtein_similarity(
        cls, s1: str, s2: str, token_sim_threshold: float = 0.8
    ) -> float:
        """
        Hybrid Jaccard-Levenshtein similarity for robust address matching.

        This method combines Jaccard similarity and Levenshtein distance to handle
        variations in address formatting and spelling. It tokenizes the input strings
        into sets of words and matches each token in the first string to the most
        similar token in the second string, provided the similarity exceeds a given
        threshold. The algorithm is particularly effective for address matching as it
        accounts for partial matches, typographical errors, and differences in token
        order, ensuring robust comparison even in noisy or inconsistent data.
        """
        s1, s2 = validate_strings(s1, s2)
        tokens1, tokens2 = list(cls._tokenize(s1)), list(cls._tokenize(s2))
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        matched_indices = set()
        match_count = 0
        for t1 in tokens1:
            best_j, best_sim = None, 0.0
            for j, t2 in enumerate(tokens2):
                if j not in matched_indices:
                    sim = cls.normalized_levenshtein_similarity(t1, t2)
                    if sim > best_sim:
                        best_j, best_sim = j, sim
            if best_j is not None and best_sim >= token_sim_threshold:
                match_count += 1
                matched_indices.add(best_j)
        union = len(tokens1) + len(tokens2) - match_count
        return match_count / union if union > 0 else 1.0


# Public API
def compute_levenshtein_similarity(s1: str, s2: str) -> float:
    """Normalized Levenshtein similarity (0.0–1.0)."""
    return SimilarityMetrics.normalized_levenshtein_similarity(s1, s2)


def compute_jaccard_similarity(s1: str, s2: str) -> float:
    """Jaccard similarity for token overlap (0.0–1.0)."""
    return SimilarityMetrics.jaccard_similarity(s1, s2)


def jaro_winkler_similarity(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
    """Jaro-Winkler similarity (0.0–1.0)."""
    return SimilarityMetrics.jaro_winkler_similarity(s1, s2, prefix_scale)


def combined_jaccard_levenshtein_similarity(
    s1: str, s2: str, token_sim_threshold: float = 0.8
) -> float:
    """Hybrid Jaccard-Levenshtein similarity for address matching (0.0–1.0)."""
    return SimilarityMetrics.combined_jaccard_levenshtein_similarity(
        s1, s2, token_sim_threshold
    )
