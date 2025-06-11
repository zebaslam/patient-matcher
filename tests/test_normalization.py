import unittest
from app.matching.normalization import _normalize_address, _normalize_phone, normalize_date, normalize_string, extract_base_address

class TestNormalization(unittest.TestCase):
    def test_extract_base_address(self):
        self.assertEqual(extract_base_address("00123 Main St Apt 4"), "123 Main St")
        self.assertEqual(extract_base_address("123 Main St Apt 4"), "123 Main St")
        self.assertEqual(extract_base_address("0456-B Elm St."), "456-B Elm St")
        self.assertEqual(extract_base_address(""), "")

    def test_normalize_date(self):
        self.assertEqual(normalize_date("02-Dec-1978"), "1978-12-02")
        self.assertEqual(normalize_date("1978-12-02"), "1978-12-02")
        self.assertEqual(normalize_date(""), "")
        self.assertEqual(normalize_date("bad-date"), "bad-date")

    def test_normalize_phone(self):
        self.assertEqual(_normalize_phone("(123) 456-7890"), "1234567890")
        self.assertEqual(_normalize_phone("512-870-9062"), "5128709062")
        self.assertEqual(_normalize_phone(""), "")

    def test_normalize_address(self):
        self.assertEqual(
            _normalize_address("00123 Main Street Apt 4"),
            "123 main st"
        )
        self.assertEqual(
            _normalize_address("0456-B Elm Boulevard, Suite 2"),
            "456-b elm blvd"
        )
        self.assertEqual(_normalize_address(""), "")

    def test_normalize_string(self):
        self.assertEqual(normalize_string("02-Dec-1978", "DOB"), "1978-12-02")
        self.assertEqual(normalize_string("(123) 456-7890", "PhoneNumber"), "1234567890")
        self.assertEqual(normalize_string("00123 Main Street Apt 4", "Address"), "123 main st")
        self.assertEqual(normalize_string("Hello, World!", "Other"), "hello world")

if __name__ == "__main__":
    unittest.main()