import unittest
from unittest.mock import patch
from app.models.patient import Patient


class DummyNormalizer:
    """
    Dummy normalization functions and constants for testing Patient normalization methods.
    Provides a static method to simulate normalization and constants for field mapping.
    """

    @staticmethod
    def normalize_string(value, field):
        """
        Simulate normalization by returning a string indicating the field and value.
        """
        return f"normalized_{field}_{value}"


PRECOMPUTED_NORMALIZATION_FIELDS = {
    "first_name": "normalized_first_name",
    "last_name": "normalized_last_name",
}
NORMALIZED_FIELDS = {"address": "normalized_address", "city": "normalized_city"}


class TestPatient(unittest.TestCase):
    """
    Unit tests for the Patient dataclass, focusing on normalization methods and field assignments.
    Uses unittest.mock.patch to replace normalization logic and constants for isolated testing.
    """

    def setUp(self):
        """
        Patch normalization functions and constants in the patient module before each test.
        """
        patcher1 = patch(
            "app.models.patient.normalize_string", DummyNormalizer.normalize_string
        )
        patcher2 = patch(
            "app.models.patient.PRECOMPUTED_NORMALIZATION_FIELDS",
            PRECOMPUTED_NORMALIZATION_FIELDS,
        )
        patcher3 = patch("app.models.patient.NORMALIZED_FIELDS", NORMALIZED_FIELDS)
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.mock_normalize_string = patcher1.start()
        self.mock_precomputed = patcher2.start()
        self.mock_normalized = patcher3.start()

    def test_patient_dataclass_fields(self):
        """
        Test that Patient dataclass fields are correctly assigned and default score is 0.0.
        """
        patient = Patient(
            patient_id="123",
            first_name="John",
            last_name="Doe",
            dob="1990-01-01",
            sex="M",
            phone_number="555-1234",
            address="123 Main St",
            city="Metropolis",
            zipcode="12345",
        )
        self.assertEqual(patient.patient_id, "123")
        self.assertEqual(patient.first_name, "John")
        self.assertEqual(patient.last_name, "Doe")
        self.assertEqual(patient.dob, "1990-01-01")
        self.assertEqual(patient.sex, "M")
        self.assertEqual(patient.phone_number, "555-1234")
        self.assertEqual(patient.address, "123 Main St")
        self.assertEqual(patient.city, "Metropolis")
        self.assertEqual(patient.zipcode, "12345")
        self.assertEqual(patient.score, 0.0)

    def test_normalize_precomputed_fields(self):
        """
        Test that normalize_precomputed_fields attaches normalized attributes for precomputed fields.
        """
        patient = Patient(
            patient_id="1",
            first_name="Alice",
            last_name="Smith",
            dob="1985-05-05",
            sex="F",
            phone_number="555-5678",
            address="456 Elm St",
            city="Gotham",
            zipcode="54321",
        )
        patient.normalize_precomputed_fields()
        self.assertTrue(hasattr(patient, "normalized_first_name"))
        self.assertTrue(hasattr(patient, "normalized_last_name"))
        self.assertEqual(
            getattr(patient, "normalized_first_name"), "normalized_first_name_Alice"
        )
        self.assertEqual(
            getattr(patient, "normalized_last_name"), "normalized_last_name_Smith"
        )

    def test_normalize_fields(self):
        """
        Test that normalize_fields attaches normalized attributes for address and city fields.
        """
        patient = Patient(
            patient_id="2",
            first_name="Bob",
            last_name="Brown",
            dob="1970-12-12",
            sex="M",
            phone_number="555-8765",
            address="789 Oak Ave",
            city="Star City",
            zipcode="67890",
        )
        patient.normalize_fields()
        self.assertTrue(hasattr(patient, "normalized_address"))
        self.assertTrue(hasattr(patient, "normalized_city"))
        self.assertEqual(
            getattr(patient, "normalized_address"), "normalized_address_789 Oak Ave"
        )
        self.assertEqual(
            getattr(patient, "normalized_city"), "normalized_city_Star City"
        )


if __name__ == "__main__":
    unittest.main()
