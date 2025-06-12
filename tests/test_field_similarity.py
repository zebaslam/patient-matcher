import unittest
from app.config import PHONE_PARTIAL_MATCH
from app.matching.field_similarity import (
    calculate_field_similarity,
    first_name_similarity,
    last_name_similarity,
    phone_similarity,
    address_similarity,
    parse_address,
    general_similarity,
)


class TestFieldSimilarity(unittest.TestCase):
    """Unit tests for field similarity functions."""

    def test_first_name_similarity(self):
        """Test similarity between first names."""
        self.assertEqual(first_name_similarity("John", "John"), 1.0)
        self.assertAlmostEqual(first_name_similarity("John", "Jon"), 0.9, places=1)
        self.assertEqual(first_name_similarity("John", "Jane"), 0.0)

    def test_last_name_similarity(self):
        """Test similarity between last names."""
        self.assertEqual(last_name_similarity("Smith", "Smith"), 1.0)
        self.assertGreater(last_name_similarity("Smith", "Smyth"), 0.8)
        self.assertEqual(last_name_similarity("Smith", "Jones"), 0.0)

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
        self.assertEqual(address_similarity("123 Main St", "123 Main St"), 1.0)
        self.assertGreater(address_similarity("123 Main St", "123 Main"), 0.0)
        self.assertGreater(address_similarity("123 Main St", "456 Main St"), 0.0)
        self.assertEqual(address_similarity("123 Main St", "456 Elm St"), 0.0)

    def test_parse_address(self):
        """Test parsing of address into number and street."""
        self.assertEqual(parse_address("123 Main St"), ("123", "main st"))
        self.assertEqual(parse_address("Main St"), ("", "st"))
        self.assertEqual(parse_address("456 Elm"), ("456", "elm"))

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


if __name__ == "__main__":
    unittest.main()
