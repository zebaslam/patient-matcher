import unittest
from app.matching.normalization import (
    _normalize_address,
    _normalize_phone,
    normalize_date,
    normalize_string,
    extract_base_address,
)


class TestNormalization(unittest.TestCase):
    """Unit tests for normalization utility functions."""

    def test_extract_base_address(self):
        """Test extraction of base address from various address formats."""
        self.assertEqual(extract_base_address("00123 Main St Apt 4"), "123 Main St")
        self.assertEqual(extract_base_address("123 Main St Apt 4"), "123 Main St")
        self.assertEqual(extract_base_address("0456-B Elm St."), "456-B Elm St")
        self.assertEqual(extract_base_address(""), "")

    def test_normalize_date(self):
        """Test normalization of date strings to standard format."""
        self.assertEqual(normalize_date("02-Dec-1978"), "1978-12-02")
        self.assertEqual(normalize_date("1978-12-02"), "1978-12-02")
        self.assertEqual(normalize_date(""), "")
        self.assertEqual(normalize_date("bad-date"), "bad-date")

    def test_normalize_phone(self):
        """Test normalization of phone numbers to digit-only strings."""
        self.assertEqual(_normalize_phone("(123) 456-7890"), "1234567890")
        self.assertEqual(_normalize_phone("512-870-9062"), "5128709062")
        self.assertEqual(_normalize_phone(""), "")

    def test_normalize_address(self):
        """Test normalization of address strings to a standard format."""
        self.assertEqual(_normalize_address("00123 Main Street Apt 4"), "123 main st")
        self.assertEqual(
            _normalize_address("0456-B Elm Boulevard, Suite 2"), "456-b elm blvd"
        )
        self.assertEqual(_normalize_address(""), "")

    def test_normalize_string(self):
        """Test normalization of strings by field type."""
        self.assertEqual(normalize_string("02-Dec-1978", "dob"), "1978-12-02")
        self.assertEqual(
            normalize_string("(123) 456-7890", "phone_number"), "1234567890"
        )
        self.assertEqual(
            normalize_string("00123 Main Street Apt 4", "address"), "123 main st"
        )
        self.assertEqual(normalize_string("Hello, World!", "other"), "hello world")


if __name__ == "__main__":
    unittest.main()
