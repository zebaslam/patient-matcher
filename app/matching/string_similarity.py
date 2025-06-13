"""String similarity algorithms for patient matching and record linkage."""

from typing import Set, Tuple


def validate_strings(s1: str, s2: str) -> Tuple[str, str]:
    """Ensure both inputs are strings and strip whitespace."""
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
                insert = prev_row[j + 1] + 1
                delete = curr_row[j] + 1
                subst = prev_row[j] + (ca != cb)
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
    def jaro_similarity(cls, s1: str, s2: str) -> float:
        """Jaro similarity (0.0–1.0), effective for short strings."""
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
        return (
            matches / len(s1)
            + matches / len(s2)
            + (matches - transpositions / 2) / matches
        ) / 3

    @classmethod
    def _find_jaro_matches(cls, s1: str, s2: str) -> Tuple[int, int]:
        """Find matches and transpositions for Jaro similarity."""
        len1, len2 = len(s1), len(s2)
        window = max(len1, len2) // 2 - 1
        window = max(0, window)
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
        if not 0 <= prefix_weight <= 0.25:
            raise ValueError("prefix_weight must be between 0 and 0.25")
        s1, s2 = validate_strings(s1, s2)
        jaro = cls.jaro_similarity(s1, s2)
        if jaro < 0.7:
            return jaro
        prefix_len = 0
        for a, b in zip(s1, s2):
            if a == b and prefix_len < 4:
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
        Each token in s1 is matched to the most similar token in s2 (above threshold).
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
            candidates = [
                (j, cls.normalized_levenshtein_similarity(t1, t2))
                for j, t2 in enumerate(tokens2)
                if j not in matched_indices
            ]
            if candidates:
                best_j, best_sim = max(candidates, key=lambda x: x[1])
                if best_sim >= token_sim_threshold:
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
