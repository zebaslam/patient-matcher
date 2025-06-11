import unittest
from app.matching import utils

class TestUtils(unittest.TestCase):
    def test_add_unique_ids(self):
        patients = [{'Name': 'A'}, {'Name': 'B'}]
        utils.add_unique_ids(patients, 'TEST')
        self.assertEqual(patients[0]['Id'], 'TEST-0')
        self.assertEqual(patients[1]['Id'], 'TEST-1')

    def test_get_patient_id(self):
        p1 = {'InternalPatientId': 'INT1'}
        p2 = {'ExternalPatientId': 'EXT1'}
        p3 = {'Id': 'GEN-1'}
        p4 = {}
        self.assertEqual(utils.get_patient_id(p1), 'INT1')
        self.assertEqual(utils.get_patient_id(p2), 'EXT1')
        self.assertEqual(utils.get_patient_id(p3), 'GEN-1')
        self.assertEqual(utils.get_patient_id(p4), utils.FALLBACK_PATIENT_ID)

    def test_extract_base_address(self):
        self.assertEqual(utils.extract_base_address("00123 Main St Apt 4"), "123 Main St")
        self.assertEqual(utils.extract_base_address("123 Main St Apt 4"), "123 Main St")
        self.assertEqual(utils.extract_base_address("0456-B Elm St."), "456-B Elm St")
        self.assertEqual(utils.extract_base_address(""), "")

    def test_normalize_date(self):
        self.assertEqual(utils.normalize_date("02-Dec-1978"), "1978-12-02")
        self.assertEqual(utils.normalize_date("1978-12-02"), "1978-12-02")
        self.assertEqual(utils.normalize_date(""), "")
        self.assertEqual(utils.normalize_date("bad-date"), "bad-date")

    def test_normalize_phone(self):
        self.assertEqual(utils._normalize_phone("(123) 456-7890"), "1234567890")
        self.assertEqual(utils._normalize_phone("512-870-9062"), "5128709062")
        self.assertEqual(utils._normalize_phone(""), "")

    def test_normalize_address(self):
        self.assertEqual(
            utils._normalize_address("00123 Main Street Apt 4"),
            "123 main st"
        )
        self.assertEqual(
            utils._normalize_address("0456-B Elm Boulevard, Suite 2"),
            "456-b elm blvd"
        )
        self.assertEqual(utils._normalize_address(""), "")

    def test_normalize_string(self):
        self.assertEqual(utils.normalize_string("02-Dec-1978", "DOB"), "1978-12-02")
        self.assertEqual(utils.normalize_string("(123) 456-7890", "PhoneNumber"), "1234567890")
        self.assertEqual(utils.normalize_string("00123 Main Street Apt 4", "Address"), "123 main st")
        self.assertEqual(utils.normalize_string("Hello, World!", "Other"), "hello world")

if __name__ == "__main__":
    unittest.main()