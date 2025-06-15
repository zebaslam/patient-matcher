import unittest
from app.config import PHONE_PARTIAL_MATCH
from app.matching.string_similarity import jaro_winkler_similarity
from app.matching.field_similarity import (
    calculate_field_similarity,
    first_name_similarity,
    phone_similarity,
    general_similarity,
)


class TestFieldSimilarity(unittest.TestCase):
    """Unit tests for field similarity functions."""

    def test_first_name_similarity(self):
        """Test similarity between first names."""
        self.assertEqual(first_name_similarity("John", "John"), 1.0)
        self.assertAlmostEqual(first_name_similarity("John", "Jon"), 0.9, places=1)
        self.assertLess(first_name_similarity("John", "Jane"), 0.8)

    def test_last_name_similarity(self):
        """Test similarity between last names."""
        self.assertEqual(
            calculate_field_similarity(
                "Smith", "Smith", "name", "last_name"
            ).similarity,
            1.0,
        )
        self.assertGreater(
            calculate_field_similarity(
                "Smith", "Smyth", "name", "last_name"
            ).similarity,
            0.8,
        )
        self.assertEqual(
            calculate_field_similarity(
                "Smith", "Jones", "name", "last_name"
            ).similarity,
            0.0,
        )

    def test_phone_similarity(self):
        """Test similarity between phone numbers."""
        self.assertEqual(phone_similarity("123-456-7890", "1234567890"), 1.0)
        self.assertEqual(
            phone_similarity("123-456-7890", "456-7890"), PHONE_PARTIAL_MATCH
        )
        self.assertGreaterEqual(phone_similarity("123-456-7890", "123-456-7891"), 0.9)
        self.assertGreater(phone_similarity("123-456-7890", "123-456-0000"), 0.0)
        self.assertEqual(phone_similarity("123-456-7890", "000-000-0000"), 0.0)

    def test_address_similarity(self):
        """Test similarity between addresses."""
        self.assertEqual(
            calculate_field_similarity(
                "123 Main St", "123 Main St", "any", "address"
            ).similarity,
            1.0,
        )
        self.assertGreater(
            calculate_field_similarity(
                "123 Main St", "123 Main", "any", "address"
            ).similarity,
            0.0,
        )
        self.assertGreater(
            calculate_field_similarity(
                "123 Main St", "456 Main St", "any", "address"
            ).similarity,
            0.0,
        )
        self.assertLess(
            calculate_field_similarity(
                "123 Main St", "456 Elm St", "any", "address"
            ).similarity,
            0.5,
        )
        self.assertLess(
            calculate_field_similarity(
                "582 Grape Port", "713 Grant Port", "any", "address"
            ).similarity,
            0.5,
        )

    def test_general_similarity(self):
        """Test general similarity between normalized strings."""
        result = general_similarity("abc", "abc")
        self.assertEqual(result.similarity, 1.0)
        self.assertEqual(result.algorithm, "levenshtein (general)")
        result = general_similarity("abc def", "abc xyz")
        self.assertGreater(result.similarity, 0.0)
        self.assertEqual(result.algorithm, "jaccard (general)")
        result = general_similarity("abc", "xyz")
        self.assertEqual(result.similarity, 0.0)
        self.assertEqual(result.algorithm, "levenshtein (general)")

    def test_calculate_field_similarity(self):
        """Test calculate_field_similarity for various field types."""
        self.assertEqual(
            calculate_field_similarity("John", "John", "name", "first_name").similarity,
            1.0,
        )
        self.assertEqual(
            calculate_field_similarity(
                "123-456-7890", "1234567890", "any", "phone_number"
            ).similarity,
            1.0,
        )
        self.assertEqual(
            calculate_field_similarity(
                "123 Main St", "123 Main St", "any", "address"
            ).similarity,
            1.0,
        )
        self.assertEqual(
            calculate_field_similarity("abc", "abc", "exact", "OtherField").similarity,
            1.0,
        )
        self.assertEqual(
            calculate_field_similarity("abc", "xyz", "exact", "OtherField").similarity,
            0.0,
        )

    def test_jaro_winkler_similarity(self):
        """Test Jaro-Winkler similarity for last names and general cases."""

        # Identical strings
        self.assertEqual(jaro_winkler_similarity("Smith", "Smith"), 1.0)
        # Similar strings
        self.assertGreater(jaro_winkler_similarity("Smith", "Smyth"), 0.8)
        # Dissimilar strings
        self.assertLess(jaro_winkler_similarity("Smith", "Jones"), 0.5)
        # Empty strings
        self.assertEqual(jaro_winkler_similarity("", ""), 1.0)
        self.assertEqual(jaro_winkler_similarity("Smith", ""), 0.0)
        self.assertEqual(jaro_winkler_similarity("", "Smith"), 0.0)

    def test_calculate_field_similarity_empty_fields(self):
        """Test that empty or None fields return similarity 0.0 and algorithm as per normalization behavior."""
        result = calculate_field_similarity("", "Smith", "name", "last_name")
        self.assertEqual(result.similarity, 0.0)
        self.assertEqual(result.algorithm, "One more fields are empty")
        result = calculate_field_similarity(None, "Smith", "name", "last_name")
        self.assertEqual(result.similarity, 0.0)
        self.assertEqual(
            result.algorithm, "jaro_winkler (last_name)"
        )  # None becomes 'none', triggers field-specific
        result = calculate_field_similarity("", "", "name", "last_name")
        self.assertEqual(result.similarity, 0.0)
        self.assertEqual(result.algorithm, "One more fields are empty")

    def test_calculate_field_similarity_exact_type(self):
        """Test that 'exact' field_type returns correct similarity and algorithm."""
        result = calculate_field_similarity("abc", "abc", "exact", "foo")
        self.assertEqual(result.similarity, 1.0)
        self.assertEqual(result.algorithm, "exact")
        result = calculate_field_similarity("abc", "xyz", "exact", "foo")
        self.assertEqual(result.similarity, 0.0)
        self.assertEqual(result.algorithm, "exact")

    def test_calculate_field_similarity_phone(self):
        """Test phone_number and phone field_name triggers phone_similarity."""
        result = calculate_field_similarity(
            "123-456-7890", "1234567890", "any", "phone_number"
        )
        self.assertEqual(result.algorithm, "exact")
        self.assertEqual(result.similarity, 1.0)
        result = calculate_field_similarity("123-456-7890", "456-7890", "any", "phone")
        self.assertEqual(result.algorithm, "levenshtein (phone)")
        self.assertEqual(result.similarity, PHONE_PARTIAL_MATCH)

    def test_calculate_field_similarity_address(self):
        """Test address field_name triggers combined_jaccard_levenshtein_similarity."""
        result = calculate_field_similarity(
            "123 Main St", "123 Main St", "any", "address"
        )
        self.assertEqual(result.algorithm, "exact")
        self.assertEqual(result.similarity, 1.0)
        result = calculate_field_similarity(
            "123 Main St", "456 Elm St", "any", "address"
        )
        self.assertEqual(result.algorithm, "combined_jaccard_levenshtein")
        self.assertLess(result.similarity, 0.5)

    def test_calculate_field_similarity_first_name(self):
        """Test first_name field_name triggers first_name_similarity."""
        result = calculate_field_similarity("John", "Jon", "name", "first_name")
        self.assertEqual(result.algorithm, "jaro_winkler (first_name)")
        self.assertGreater(result.similarity, 0.8)
        result = calculate_field_similarity("John", "John", "name", "first_name")
        self.assertEqual(result.algorithm, "exact")
        self.assertEqual(result.similarity, 1.0)
        result = calculate_field_similarity("John", "Jane", "name", "first_name")
        self.assertEqual(result.algorithm, "jaro_winkler (first_name)")
        self.assertLess(result.similarity, 0.8)

    def test_calculate_field_similarity_last_name(self):
        """Test last_name field_name triggers jaro_winkler_similarity."""
        result = calculate_field_similarity("Smith", "Smyth", "name", "last_name")
        self.assertEqual(result.algorithm, "jaro_winkler (last_name)")
        self.assertGreater(result.similarity, 0.8)
        result = calculate_field_similarity("Smith", "Smith", "name", "last_name")
        self.assertEqual(result.algorithm, "exact")
        self.assertEqual(result.similarity, 1.0)
        result = calculate_field_similarity("Smith", "Jones", "name", "last_name")
        self.assertEqual(result.algorithm, "jaro_winkler (last_name)")
        self.assertLess(result.similarity, 0.5)

    def test_calculate_field_similarity_general(self):
        """Test fallback to general_similarity for other fields."""
        result = calculate_field_similarity("foo bar", "foo baz", "text", "notes")
        self.assertEqual(result.algorithm, "jaccard (general)")
        self.assertGreater(result.similarity, 0.0)
        result = calculate_field_similarity("abc", "abc", "text", "notes")
        self.assertEqual(result.algorithm, "exact")
        self.assertEqual(result.similarity, 1.0)
        result = calculate_field_similarity("abc", "xyz", "text", "notes")
        self.assertEqual(result.algorithm, "levenshtein (general)")
        self.assertEqual(result.similarity, 0.0)


if __name__ == "__main__":
    unittest.main()
