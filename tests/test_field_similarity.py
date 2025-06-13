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
            calculate_field_similarity("Smith", "Smith", "name", "last_name"), 1.0
        )
        self.assertGreater(
            calculate_field_similarity("Smith", "Smyth", "name", "last_name"), 0.8
        )
        self.assertEqual(
            calculate_field_similarity("Smith", "Jones", "name", "last_name"), 0.0
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
            calculate_field_similarity("123 Main St", "123 Main St", "any", "address"),
            1.0,
        )
        self.assertGreater(
            calculate_field_similarity("123 Main St", "123 Main", "any", "address"), 0.0
        )
        self.assertGreater(
            calculate_field_similarity("123 Main St", "456 Main St", "any", "address"),
            0.0,
        )
        self.assertLess(
            calculate_field_similarity("123 Main St", "456 Elm St", "any", "address"),
            0.5,
        )
        self.assertLess(
            calculate_field_similarity(
                "582 Grape Port", "713 Grant Port", "any", "address"
            ),
            0.5,
        )

    def test_general_similarity(self):
        """Test general similarity between normalized strings."""
        self.assertEqual(general_similarity("abc", "abc"), 1.0)
        self.assertGreater(general_similarity("abc def", "abc xyz"), 0.0)
        self.assertEqual(general_similarity("abc", "xyz"), 0.0)

    def test_calculate_field_similarity(self):
        """Test calculate_field_similarity for various field types."""
        self.assertEqual(
            calculate_field_similarity("John", "John", "name", "first_name"), 1.0
        )
        self.assertEqual(
            calculate_field_similarity(
                "123-456-7890", "1234567890", "any", "phone_number"
            ),
            1.0,
        )
        self.assertEqual(
            calculate_field_similarity("123 Main St", "123 Main St", "any", "address"),
            1.0,
        )
        self.assertEqual(
            calculate_field_similarity("abc", "abc", "exact", "OtherField"), 1.0
        )
        self.assertEqual(
            calculate_field_similarity("abc", "xyz", "exact", "OtherField"), 0.0
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


if __name__ == "__main__":
    unittest.main()
