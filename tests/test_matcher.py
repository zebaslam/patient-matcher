import unittest
from unittest.mock import patch
from app.models.patient import Patient  # Import the real Patient class

from app.matching.matcher import match_patients, _normalized_fields_identical


class DummyPatient(Patient):  # Inherit from Patient for type compatibility
    """A dummy patient for testing."""

    def __init__(self, **fields):
        super().__init__(
            patient_id="",
            first_name="",
            last_name="",
            dob="",
            sex="",
            phone_number="",
            address="",
            city="",
            zipcode="",
        )  # Provide empty string for all required parameters
        for k, v in fields.items():
            setattr(self, k, v)
        self.normalized = False

    def normalize_precomputed_fields(self):
        self.normalized = True


class TestMatcher(unittest.TestCase):
    """Test suite for patient matcher."""

    def test_normalized_fields_identical_true(self):
        """Test identical normalized fields returns True."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS",
            {"dob": "dob_norm", "sex": "sex_norm"},
        ):
            p1 = DummyPatient(dob_norm="1990-01-01", sex_norm="M")
            p2 = DummyPatient(dob_norm="1990-01-01", sex_norm="M")
            self.assertTrue(_normalized_fields_identical(p1, p2))

    def test_normalized_fields_identical_false(self):
        """Test differing normalized fields returns False."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS",
            {"dob": "dob_norm", "sex": "sex_norm"},
        ):
            p1 = DummyPatient(dob_norm="1990-01-01", sex_norm="M")
            p2 = DummyPatient(dob_norm="1990-01-01", sex_norm="F")
            self.assertFalse(_normalized_fields_identical(p1, p2))

    def test_normalized_fields_identical_empty_fields(self):
        """Test empty normalized fields returns True."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS",
            {"dob": "dob_norm", "sex": "sex_norm"},
        ):
            p1 = DummyPatient(dob_norm="", sex_norm="")
            p2 = DummyPatient(dob_norm="", sex_norm="")
            self.assertTrue(_normalized_fields_identical(p1, p2))

    def test_match_patients_match(self):
        """Test match_patients returns a match when similarity is above threshold."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS", {"dob": "dob_norm"}
        ), patch("app.matching.matcher.MATCH_THRESHOLD", 0.8), patch(
            "app.matching.matcher.calculate_weighted_similarity"
        ) as mock_calc_sim:
            p1 = DummyPatient(dob_norm="1990-01-01")
            p2 = DummyPatient(dob_norm="1990-01-01")
            mock_calc_sim.return_value = (0.9, {"dob": 1.0})

            matches = match_patients([p1], [p2])
            self.assertEqual(len(matches), 1)
            self.assertIs(matches[0]["external"], p2)
            self.assertIs(matches[0]["internal"], p1)
            self.assertEqual(matches[0]["score"], 0.9)
            self.assertEqual(matches[0]["breakdown"], {"dob": 1.0})
            self.assertTrue(p1.normalized)
            self.assertTrue(p2.normalized)

    def test_match_patients_no_match_due_to_fields(self):
        """Test match_patients returns no match if normalized fields differ."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS", {"dob": "dob_norm"}
        ), patch("app.matching.matcher.MATCH_THRESHOLD", 0.8), patch(
            "app.matching.matcher.calculate_weighted_similarity"
        ) as mock_calc_sim:
            p1 = DummyPatient(dob_norm="1990-01-01")
            p2 = DummyPatient(dob_norm="2000-01-01")
            mock_calc_sim.return_value = (0.95, {"dob": 1.0})

            matches = match_patients([p1], [p2])
            self.assertEqual(matches, [])

    def test_match_patients_no_match_due_to_threshold(self):
        """Test match_patients returns no match if similarity is below threshold."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS", {"dob": "dob_norm"}
        ), patch("app.matching.matcher.MATCH_THRESHOLD", 0.8), patch(
            "app.matching.matcher.calculate_weighted_similarity"
        ) as mock_calc_sim:
            p1 = DummyPatient(dob_norm="1990-01-01")
            p2 = DummyPatient(dob_norm="1990-01-01")
            mock_calc_sim.return_value = (0.5, {"dob": 0.5})

            matches = match_patients([p1], [p2])
            self.assertEqual(matches, [])

    def test_match_patients_empty_lists(self):
        """Test match_patients returns empty list for empty inputs."""
        self.assertEqual(match_patients([], []), [])
        self.assertEqual(match_patients([DummyPatient(dob_norm="1990-01-01")], []), [])
        self.assertEqual(match_patients([], [DummyPatient(dob_norm="1990-01-01")]), [])


if __name__ == "__main__":
    unittest.main()
