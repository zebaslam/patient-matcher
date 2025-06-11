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

if __name__ == "__main__":
    unittest.main()