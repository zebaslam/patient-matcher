import unittest
from app.matching import string_similarity


class TestSimilarityMetrics(unittest.TestCase):
    """Unit tests for string similarity functions."""

    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation."""
        self.assertEqual(string_similarity.levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(string_similarity.levenshtein_distance("flaw", "lawn"), 2)
        self.assertEqual(string_similarity.levenshtein_distance("", ""), 0)
        self.assertEqual(string_similarity.levenshtein_distance("abc", ""), 3)
        self.assertEqual(string_similarity.levenshtein_distance("", "abc"), 3)
        self.assertEqual(string_similarity.levenshtein_distance("abc", "abc"), 0)

    def test_normalized_similarity(self):
        """Test normalized similarity ratio calculation."""
        self.assertAlmostEqual(
            string_similarity.similarity_ratio("kitten", "sitting"), 1 - 3 / 7
        )
        self.assertEqual(string_similarity.similarity_ratio("", ""), 1.0)
        self.assertEqual(string_similarity.similarity_ratio("abc", ""), 0.0)
        self.assertEqual(string_similarity.similarity_ratio("", "abc"), 0.0)
        self.assertEqual(string_similarity.similarity_ratio("abc", "abc"), 1.0)

    def test_jaccard_similarity(self):
        """Test Jaccard (token overlap) similarity calculation."""
        self.assertEqual(
            string_similarity.token_overlap_score("the cat", "the cat"), 1.0
        )
        self.assertEqual(
            string_similarity.token_overlap_score("the cat", "the dog"), 1 / 3
        )
        self.assertEqual(string_similarity.token_overlap_score("", ""), 1.0)
        self.assertEqual(string_similarity.token_overlap_score("a b c", ""), 0.0)
        self.assertEqual(string_similarity.token_overlap_score("", "a b c"), 0.0)

    def test_jaro_similarity(self):
        """Test Jaro similarity calculation."""
        self.assertAlmostEqual(
            string_similarity.jaro_similarity("MARTHA", "MARHTA"), 0.944, places=3
        )
        self.assertAlmostEqual(
            string_similarity.jaro_similarity("DWAYNE", "DUANE"), 0.822, places=3
        )
        self.assertAlmostEqual(
            string_similarity.jaro_similarity("ALAN", "ALLEN"), 0.783, places=3
        )
        self.assertEqual(string_similarity.jaro_similarity("", ""), 1.0)
        self.assertEqual(string_similarity.jaro_similarity("abc", ""), 0.0)
        self.assertEqual(string_similarity.jaro_similarity("", "abc"), 0.0)
        self.assertEqual(string_similarity.jaro_similarity("abc", "abc"), 1.0)

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


if __name__ == "__main__":
    unittest.main()
