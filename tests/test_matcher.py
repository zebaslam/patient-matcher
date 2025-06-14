import unittest
from unittest.mock import patch
from app.models.patient import Patient

from app.matching.matcher import match_patients


class DummyPatient(Patient):  # Inherit from Patient for type compatibility
    """A dummy patient for testing."""

    def __init__(self, **fields):
        self.normalized = False  # Set before super().__init__
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

    def normalize_precomputed_fields(self):
        self.normalized = True


class TestMatcher(unittest.TestCase):
    """Test suite for patient matcher."""

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
            match = matches[0]
            self.assertIs(match.external, p2)
            self.assertIs(match.internal, p1)
            self.assertEqual(match.score, 0.9)
            self.assertEqual(match.breakdown, {"dob": 1.0})
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

    def test_match_patients_single_best_match(self):
        """Test match_patients returns only the single best match per external patient."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS",
            {"dob": "dob_norm", "sex": "sex_norm"},
        ), patch("app.matching.matcher.MATCH_THRESHOLD", 0.7), patch(
            "app.matching.matcher.calculate_weighted_similarity"
        ) as mock_calc_sim:
            # Use lowercased 'm' to match normalization of external patient
            p1 = DummyPatient(dob_norm="1990-01-01", sex_norm="m")
            p2 = DummyPatient(dob_norm="1990-01-01", sex_norm="m")
            p3 = DummyPatient(dob_norm="1990-01-01", sex_norm="m")
            external = [
                Patient(
                    patient_id="1",
                    first_name="John",
                    last_name="Doe",
                    dob="1990-01-01",
                    sex="M",
                    phone_number="1234567890",
                    address="123 Street",
                    city="City",
                    zipcode="12345",
                )
            ]

            # Simulate different similarity scores for each internal patient
            def sim_func(_, internal):
                if internal is p1:
                    return (0.8, {"dob": 1.0})
                if internal is p2:
                    return (0.85, {"dob": 1.0})  # best match
                if internal is p3:
                    return (0.7, {"dob": 1.0})

            mock_calc_sim.side_effect = sim_func

            matches = match_patients([p1, p2, p3], external)
            self.assertEqual(len(matches), 1)
            match = matches[0]
            self.assertEqual(match.score, 0.85)
            self.assertEqual(match.breakdown, {"dob": 1.0})
            self.assertIs(match.external, external[0])
            self.assertIs(match.internal, p2)

    def test_match_patients_no_internal_patients(self):
        """Test match_patients returns empty list if internal list is empty."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS",
            {"dob": "dob_norm"},
        ), patch("app.matching.matcher.MATCH_THRESHOLD", 0.8), patch(
            "app.matching.matcher.calculate_weighted_similarity"
        ):
            external = [
                Patient(
                    patient_id="1",
                    first_name="John",
                    last_name="Doe",
                    dob="1990-01-01",
                    sex="M",
                    phone_number="1234567890",
                    address="123 Street",
                    city="City",
                    zipcode="12345",
                )
            ]
            matches = match_patients([], external)
            self.assertEqual(matches, [])

    def test_match_patients_no_external_patients(self):
        """Test match_patients returns empty list if external list is empty."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS",
            {"dob": "dob_norm"},
        ), patch("app.matching.matcher.MATCH_THRESHOLD", 0.8), patch(
            "app.matching.matcher.calculate_weighted_similarity"
        ):
            internal = [
                Patient(
                    patient_id="2",
                    first_name="Jane",
                    last_name="Smith",
                    dob="1990-01-01",
                    sex="F",
                    phone_number="9876543210",
                    address="456 Avenue",
                    city="Town",
                    zipcode="67890",
                )
            ]
            matches = match_patients(internal, [])
            self.assertEqual(matches, [])

    def test_match_patients_calls_normalize_precomputed_fields(self):
        """Test that normalize_precomputed_fields is called for all patients."""
        with patch(
            "app.matching.matcher.PRECOMPUTED_NORMALIZATION_FIELDS",
            {"dob": "dob_norm"},
        ), patch("app.matching.matcher.MATCH_THRESHOLD", 0.8), patch(
            "app.matching.matcher.calculate_weighted_similarity"
        ) as mock_calc_sim:
            p1 = DummyPatient(dob_norm="1990-01-01")
            p2 = DummyPatient(dob_norm="1990-01-01")
            mock_calc_sim.return_value = (0.9, {"dob": 1.0})

            match_patients([p1], [p2])
            self.assertTrue(p1.normalized)
            self.assertTrue(p2.normalized)


if __name__ == "__main__":
    unittest.main()
