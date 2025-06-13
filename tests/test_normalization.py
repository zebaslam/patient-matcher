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

    def test_extract_base_address_variants(self):
        """Test extract_base_address with more variants and edge cases."""
        self.assertEqual(
            extract_base_address("00001 Oak Place, Suite 101"), "1 Oak Place"
        )
        self.assertEqual(extract_base_address("00000 Maple Ave."), "0 Maple Ave")
        self.assertEqual(extract_base_address("789 Pine Dr."), "789 Pine Dr")
        self.assertEqual(extract_base_address("456 Cedar Ct, Apt 12B"), "456 Cedar Ct")
        self.assertEqual(extract_base_address("12 Spruce Blvd."), "12 Spruce Blvd")
        self.assertEqual(extract_base_address("00000"), "0")
        self.assertEqual(extract_base_address("Apt 4"), "")

    def test_normalize_date_edge_cases(self):
        """Test normalize_date with edge cases and invalid formats."""
        self.assertEqual(normalize_date("2-Dec-1978"), "1978-12-02")
        self.assertEqual(normalize_date("31-Feb-2000"), "31-Feb-2000")  # Invalid date
        self.assertEqual(normalize_date(" 02-Dec-1978 "), "1978-12-02")
        self.assertEqual(normalize_date("12/31/1999"), "12/31/1999")

    def test_normalize_phone_edge_cases(self):
        """Test _normalize_phone with edge cases."""
        self.assertEqual(_normalize_phone("+1 (800) 555-0199"), "18005550199")
        self.assertEqual(_normalize_phone("ext. 1234"), "1234")
        self.assertEqual(_normalize_phone("abc-def-ghij"), "")

    def test_normalize_address_abbreviations_and_typos(self):
        """Test _normalize_address with various abbreviations and typos."""
        self.assertEqual(_normalize_address("123 Main Stret"), "123 main st")
        self.assertEqual(_normalize_address("456 North Avenue"), "456 n ave")
        self.assertEqual(_normalize_address("789 South Boulevard"), "789 s blvd")
        self.assertEqual(_normalize_address("101 West Drive"), "101 w dr")
        self.assertEqual(_normalize_address("202 East Place"), "202 e pl")
        self.assertEqual(_normalize_address("303 Court"), "303 ct")
        self.assertEqual(_normalize_address("404 Suite"), "404 ste")

    def test_normalize_string_general(self):
        """Test normalize_string with general strings and unknown field names."""
        self.assertEqual(
            normalize_string("  Hello,   World!  ", "unknown"), "hello world"
        )
        self.assertEqual(normalize_string("Test@String#123", "random"), "teststring123")
        self.assertEqual(normalize_string("", "address"), "")
        self.assertEqual(normalize_string("APT 5", "address"), "apt 5")

    def test_normalize_address_directional_abbreviations(self):
        """Test that directional words are correctly abbreviated in addresses."""
        self.assertEqual(_normalize_address("123 North Main Street"), "123 n main st")
        self.assertEqual(_normalize_address("456 South Elm Avenue"), "456 s elm ave")
        self.assertEqual(_normalize_address("789 East Oak Boulevard"), "789 e oak blvd")
        self.assertEqual(_normalize_address("101 West Pine Drive"), "101 w pine dr")
        self.assertEqual(_normalize_address("202 north place"), "202 n pl")
        self.assertEqual(_normalize_address("303 SOUTH court"), "303 s ct")
        self.assertEqual(_normalize_address("404 east suite"), "404 e ste")


if __name__ == "__main__":
    unittest.main()
