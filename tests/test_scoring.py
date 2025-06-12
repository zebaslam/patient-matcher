import unittest
from unittest.mock import patch
from app.matching import scoring
from app.models.patient import Patient

# Disable protected member access warnings for test methods
# pylint: disable=protected-access


class DummyPatient(Patient):
    """
    Dummy patient class for testing scoring functions.
    Ensures all normalized fields exist as attributes, defaulting to None.
    """

    def __init__(self, **kwargs):
        # Provide default values for all required Patient fields
        super().__init__(
            patient_id=kwargs.get("patient_id", ""),
            first_name=kwargs.get("first_name", ""),
            last_name=kwargs.get("last_name", ""),
            dob=kwargs.get("dob", ""),
            sex=kwargs.get("sex", ""),
            phone_number=kwargs.get("phone_number", ""),
            address=kwargs.get("address", ""),
            city=kwargs.get("city", ""),
            zipcode=kwargs.get("zipcode", ""),
        )
        normalized_fields = [
            "first_name_norm",
            "last_name_norm",
            "dob_norm",
            "sex_norm",
        ]
        for field in normalized_fields:
            setattr(self, field, kwargs.get(field, None))
        # Set any other attributes provided in kwargs
        for k, v in kwargs.items():
            if k not in normalized_fields:
                setattr(self, k, v)

    def normalize_fields(self, *args, **kwargs):
        """
        Dummy normalize_fields method for compatibility.
        """


class TestScoring(unittest.TestCase):
    """
    Unit tests for the scoring module in app.matching.
    Tests weighted similarity, penalties, and normalized value extraction.
    """

    def setUp(self):
        """
        Set up patchers for module-level constants and test configuration.
        """
        self.field_weights = {"first_name": 2.0, "last_name": 2.0, "dob": 3.0}
        self.field_types = {
            "first_name": "string",
            "last_name": "string",
            "dob": "date",
        }
        self.penalties = {"dob": 0.1}
        self.critical_fields = ["dob"]
        self.normalized_fields = {
            "first_name": "first_name_norm",
            "last_name": "last_name_norm",
            "dob": "dob_norm",
        }
        patcher1 = patch("app.matching.scoring.FIELD_WEIGHTS", self.field_weights)
        patcher2 = patch("app.matching.scoring.FIELD_TYPES", self.field_types)
        patcher4 = patch("app.matching.scoring.CRITICAL_FIELDS", self.critical_fields)
        patcher5 = patch(
            "app.matching.scoring.NORMALIZED_FIELDS", self.normalized_fields
        )
        patcher7 = patch("app.matching.scoring.DEFAULT_SIMILARITY", 0.0)
        self.patchers = [
            patcher1,
            patcher2,
            patcher4,
            patcher5,
            patcher7,
        ]
        for p in self.patchers:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self.patchers])

    @patch("app.matching.scoring.calculate_field_similarity")
    def test_all_fields_partial_match(self, mock_sim):
        """
        Test that partial similarity across all fields results in a score between 0 and 1,
        and that all fields are included in the breakdown.
        """
        mock_sim.side_effect = [0.5, 0.7, 0.8]
        p1 = DummyPatient(
            first_name_norm="Jon", last_name_norm="Dae", dob_norm="1990-01-01"
        )
        p2 = DummyPatient(
            first_name_norm="John", last_name_norm="Doe", dob_norm="1990-01-02"
        )
        score, details = scoring.calculate_weighted_similarity(p1, p2)
        self.assertTrue(0 < score < 1)
        self.assertIn("fields", details)
        self.assertEqual(len(details["fields"]), 3)

    @patch("app.matching.scoring.calculate_field_similarity")
    def test_no_fields_match(self, mock_sim):
        """
        Test that when all similarities are zero, the score is zero and early_exit is set in details.
        """
        mock_sim.return_value = 0.0
        p1 = DummyPatient(first_name_norm="A", last_name_norm="B", dob_norm="C")
        p2 = DummyPatient(first_name_norm="X", last_name_norm="Y", dob_norm="Z")
        score, details = scoring.calculate_weighted_similarity(p1, p2)
        self.assertEqual(score, 0.0)
        self.assertIn("early_exit", details)

    @patch("app.matching.scoring.calculate_field_similarity")
    def test_missing_fields_in_one_patient(self, mock_sim):
        """
        Test that missing fields in one patient are handled correctly in the breakdown.
        """
        mock_sim.return_value = 1.0
        p1 = DummyPatient(
            first_name_norm="John", last_name_norm=None, dob_norm="1990-01-01"
        )
        p2 = DummyPatient(
            first_name_norm="John", last_name_norm="Doe", dob_norm="1990-01-01"
        )
        _, details = scoring.calculate_weighted_similarity(p1, p2)
        self.assertIn("first_name", details["fields"])
        self.assertIn("dob", details["fields"])
        self.assertNotIn("last_name", details["fields"])

    def test__get_normalized_precompute_values_missing_norm(self):
        """
        Test that _get_normalized_precompute_values falls back to field_name_norm if not in NORMALIZED_FIELDS.
        """
        p1 = DummyPatient(sex_norm="bar")
        p2 = DummyPatient(sex_norm="baz")
        n1, n2 = scoring._get_normalized_precompute_values(p1, p2, "sex")
        self.assertEqual(n1, "bar")
        self.assertEqual(n2, "baz")

    def test__update_breakdown_and_score_zero_weight(self):
        """
        Test that _update_breakdown_and_score returns zero weighted score when weight is zero.
        """
        breakdown = {}
        wscore = scoring._update_breakdown_and_score(breakdown, "foo", 0.5, 0.0)
        self.assertEqual(breakdown["foo"]["weighted_score"], 0.0)
        self.assertEqual(wscore, 0.0)


if __name__ == "__main__":
    unittest.main()
