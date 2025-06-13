import unittest
from app.matching import string_similarity
from app.matching import normalization

# Disable protected member access warnings for test methods
# pylint: disable=protected-access


class TestStringSimilarityMetrics(unittest.TestCase):
    """Unit tests for string similarity functions."""

    def test_normalized_similarity(self):
        """Test normalized similarity ratio calculation."""
        self.assertAlmostEqual(
            string_similarity.levenshtein_similarity("kitten", "sitting"),
            1 - 3 / 7,
        )
        self.assertEqual(string_similarity.levenshtein_similarity("", ""), 1.0)
        self.assertEqual(string_similarity.levenshtein_similarity("abc", ""), 0.0)
        self.assertEqual(string_similarity.levenshtein_similarity("", "abc"), 0.0)
        self.assertEqual(string_similarity.levenshtein_similarity("abc", "abc"), 1.0)

    def test_jaccard_similarity(self):
        """Test Jaccard (token overlap) similarity calculation."""
        self.assertEqual(
            string_similarity.jaccard_similarity("the cat", "the cat"), 1.0
        )
        self.assertEqual(
            string_similarity.jaccard_similarity("the cat", "the dog"), 1 / 3
        )
        self.assertEqual(string_similarity.jaccard_similarity("", ""), 1.0)
        self.assertEqual(string_similarity.jaccard_similarity("a b c", ""), 0.0)
        self.assertEqual(string_similarity.jaccard_similarity("", "a b c"), 0.0)

    def test_jaro_winkler_similarity(self):
        """Test Jaro-Winkler similarity calculation."""
        self.assertAlmostEqual(
            string_similarity.jaro_winkler_similarity("MARTHA", "MARHTA"),
            0.961,
            places=3,
        )
        self.assertAlmostEqual(
            string_similarity.jaro_winkler_similarity("DWAYNE", "DUANE"), 0.84, places=2
        )
        self.assertAlmostEqual(
            string_similarity.jaro_winkler_similarity("ALAN", "ALLEN"), 0.827, places=3
        )
        self.assertEqual(string_similarity.jaro_winkler_similarity("", ""), 1.0)
        self.assertEqual(string_similarity.jaro_winkler_similarity("abc", ""), 0.0)
        self.assertEqual(string_similarity.jaro_winkler_similarity("", "abc"), 0.0)
        self.assertEqual(string_similarity.jaro_winkler_similarity("abc", "abc"), 1.0)

    def test_combined_jaccard_levenshtein_similarity(self):
        """Test hybrid Jaccard-Levenshtein similarity for address matching."""
        sim = string_similarity.combined_jaccard_levenshtein_similarity

        # Identical addresses
        self.assertEqual(sim("123 Main St", "123 Main St"), 1.0)

        # Completely different
        self.assertEqual(sim("123 Main St", "456 Elm Ave"), 0.0)

        # Empty strings
        self.assertEqual(sim("", ""), 1.0)
        self.assertEqual(sim("abc", ""), 0.0)
        self.assertEqual(sim("", "abc"), 0.0)

        # Abbreviation vs full (lower threshold to allow "St" ~ "Street")
        h1 = normalization._normalize_address("123 Main St")
        h2 = normalization._normalize_address("123 Main Street")
        h3 = normalization._normalize_address("123 Main Street Apt 4")
        self.assertGreater(
            sim(h1, h2, token_sim_threshold=0.5),
            0.5,
        )

        # Extra tokens
        self.assertGreater(sim(h2, h3, token_sim_threshold=0.5), 0.5)


if __name__ == "__main__":
    unittest.main()
