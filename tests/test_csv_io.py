"""
Unit tests for CSV IO functions, including loading patient data from CSV files.
"""

import unittest
from unittest.mock import patch
from app.io import csv_io
from app.models.patient import Patient


def get_fake_patients():
    """Return a list of two fake Patient objects for testing purposes."""
    return [
        Patient(
            patient_id="1",
            first_name="John",
            last_name="Doe",
            dob="1990-01-01",
            sex="M",
            phone_number="1234567890",
            address="123 Main St",
            city="Metropolis",
            zipcode="12345",
        ),
        Patient(
            patient_id="2",
            first_name="Jane",
            last_name="Smith",
            dob="1985-05-05",
            sex="F",
            phone_number="0987654321",
            address="456 Elm St",
            city="Gotham",
            zipcode="54321",
        ),
    ]


class TestCsvIo(unittest.TestCase):
    """Unit tests for csv_io.load_data and related CSV IO logic."""

    def setUp(self):
        """Set up fake patient data for each test."""
        self.fake_patients = get_fake_patients()

    @patch("app.io.csv_io.load_patients")
    def test_load_data_returns_internal_and_external_lists(self, mock_load_patients):
        """Test that load_data returns correct internal and external patient lists."""
        # Arrange
        mock_load_patients.side_effect = [self.fake_patients, self.fake_patients[::-1]]
        # Act
        internal, external = csv_io.load_data()
        # Assert
        self.assertEqual(internal, self.fake_patients)
        self.assertEqual(external, self.fake_patients[::-1])
        self.assertEqual(mock_load_patients.call_count, 2)
        mock_load_patients.assert_any_call(
            csv_io.INTERNAL_CSV_PATH, "InternalPatientId"
        )
        mock_load_patients.assert_any_call(
            csv_io.EXTERNAL_CSV_PATH, "ExternalPatientId"
        )

    @patch("app.io.csv_io.load_patients")
    def test_load_data_handles_empty_lists(self, mock_load_patients):
        """Test that load_data returns empty lists when no data is loaded."""
        mock_load_patients.side_effect = [[], []]
        internal, external = csv_io.load_data()
        self.assertEqual(internal, [])
        self.assertEqual(external, [])


if __name__ == "__main__":
    unittest.main()
