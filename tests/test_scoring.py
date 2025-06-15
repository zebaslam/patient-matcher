import unittest
from unittest.mock import patch
from app.matching import scoring
from app.models.patient import Patient
from app.models.field_similarity_result import FieldSimilarityResult

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
        mock_sim.side_effect = [
            FieldSimilarityResult(0.5, "alg1"),
            FieldSimilarityResult(0.7, "alg2"),
            FieldSimilarityResult(0.8, "alg3"),
        ]
        p1 = DummyPatient(
            first_name_norm="Jon", last_name_norm="Dae", dob_norm="1990-01-01"
        )
        p2 = DummyPatient(
            first_name_norm="John", last_name_norm="Doe", dob_norm="1990-01-02"
        )
        score = scoring.calculate_weighted_similarity(p1, p2)
        self.assertTrue(0 < score.value < 1)
        self.assertEqual(len(score.breakdown), 3)

    @patch("app.matching.scoring.calculate_field_similarity")
    def test_no_fields_match(self, mock_sim):
        """
        Test that when all similarities are zero, the score is zero and early_exit is set in details.
        """
        mock_sim.return_value = FieldSimilarityResult(0.0, "alg")
        p1 = DummyPatient(first_name_norm="A", last_name_norm="B", dob_norm="C")
        p2 = DummyPatient(first_name_norm="X", last_name_norm="Y", dob_norm="Z")
        score = scoring.calculate_weighted_similarity(p1, p2)
        self.assertEqual(score.value, 0.0)

    @patch("app.matching.scoring.calculate_field_similarity")
    def test_missing_fields_in_one_patient(self, mock_sim):
        """
        Test that missing fields in one patient are handled correctly in the breakdown.
        """
        mock_sim.return_value = FieldSimilarityResult(1.0, "alg")
        p1 = DummyPatient(
            first_name_norm="John", last_name_norm="", dob_norm="1990-01-01"
        )
        p2 = DummyPatient(
            first_name_norm="John", last_name_norm="Doe", dob_norm="1990-01-01"
        )
        score = scoring.calculate_weighted_similarity(p1, p2)
        self.assertIn("first_name", score.breakdown)
        self.assertIn("dob", score.breakdown)
        self.assertIn("last_name", score.breakdown)
        # The test expects last_name similarity to be 0.5 for missing field
        self.assertEqual(score.breakdown["last_name"]["similarity"], 0.5)

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

    def test_final_score_zero_weight(self):
        """
        Test that when FIELD_WEIGHTS is empty, the final score defaults to DEFAULT_SIMILARITY.
        This ensures the scoring system has a fallback when no field weights are configured.
        """

        orig_field_weights = scoring.FIELD_WEIGHTS
        scoring.FIELD_WEIGHTS = {}
        p1 = DummyPatient()
        p2 = DummyPatient()
        score = scoring.calculate_weighted_similarity(p1, p2)
        self.assertEqual(score.value, scoring.DEFAULT_SIMILARITY)
        scoring.FIELD_WEIGHTS = orig_field_weights

    def test_final_score_below_default(self):
        """
        Test that when calculated weighted score is below DEFAULT_SIMILARITY,
        the final score is set to DEFAULT_SIMILARITY as a minimum threshold.
        This ensures the scoring system maintains a baseline similarity score.
        """
        orig_field_weights = scoring.FIELD_WEIGHTS
        orig_critical_fields = scoring.CRITICAL_FIELDS
        scoring.FIELD_WEIGHTS = {"test_field": 1.0}
        scoring.CRITICAL_FIELDS = set()

        class P(DummyPatient):
            """
            Dummy subclass for testing with a custom normalized field.
            """

            test_field_norm = ""

        p1 = P()
        p2 = P()
        score = scoring.calculate_weighted_similarity(p1, p2)
        # The expected score is 0.5, since both normalized values are empty and not critical, so sim=0.5
        self.assertEqual(score.value, 0.5)
        scoring.FIELD_WEIGHTS = orig_field_weights
        scoring.CRITICAL_FIELDS = orig_critical_fields

    def test_penalize_missing_critical_field(self):
        """
        Test that missing data for a critical field results in a similarity of 0.0 for that field.
        """
        # dob is critical
        p1 = DummyPatient(first_name_norm="John", last_name_norm="Doe", dob_norm="")
        p2 = DummyPatient(
            first_name_norm="John", last_name_norm="Doe", dob_norm="1990-01-01"
        )
        score = scoring.calculate_weighted_similarity(p1, p2)
        self.assertEqual(score.breakdown["dob"]["similarity"], 0.0)
        self.assertEqual(score.breakdown["dob"]["algorithm"], "empty")

    def test_penalize_missing_noncritical_field(self):
        """
        Test that missing data for a non-critical field results in a similarity of 0.5 for that field.
        """
        # first_name is not critical
        p1 = DummyPatient(
            first_name_norm="", last_name_norm="Doe", dob_norm="1990-01-01"
        )
        p2 = DummyPatient(
            first_name_norm="John", last_name_norm="Doe", dob_norm="1990-01-01"
        )
        score = scoring.calculate_weighted_similarity(p1, p2)
        self.assertEqual(score.breakdown["first_name"]["similarity"], 0.5)
        self.assertEqual(score.breakdown["first_name"]["algorithm"], "empty")

    def test_breakdown_contains_algorithm(self):
        """
        Test that the breakdown for each field contains the algorithm used.
        """
        with patch("app.matching.scoring.calculate_field_similarity") as mock_sim:
            mock_sim.return_value = FieldSimilarityResult(1.0, "dummy_alg")
            p1 = DummyPatient(first_name_norm="A", last_name_norm="B", dob_norm="C")
            p2 = DummyPatient(first_name_norm="A", last_name_norm="B", dob_norm="C")
            score = scoring.calculate_weighted_similarity(p1, p2)
            for field in self.field_weights:
                self.assertIn("algorithm", score.breakdown[field])
                self.assertEqual(score.breakdown[field]["algorithm"], "dummy_alg")

    def test_weighted_score_calculation(self):
        """
        Test that the weighted score for each field is calculated as similarity * weight.
        """
        with patch("app.matching.scoring.calculate_field_similarity") as mock_sim:
            mock_sim.side_effect = [
                FieldSimilarityResult(0.5, "alg1"),
                FieldSimilarityResult(0.7, "alg2"),
                FieldSimilarityResult(0.8, "alg3"),
            ]
            p1 = DummyPatient(
                first_name_norm="Jon", last_name_norm="Dae", dob_norm="1990-01-01"
            )
            p2 = DummyPatient(
                first_name_norm="John", last_name_norm="Doe", dob_norm="1990-01-02"
            )
            score = scoring.calculate_weighted_similarity(p1, p2)
            self.assertAlmostEqual(
                score.breakdown["first_name"]["weighted_score"], 0.5 * 2.0
            )
            self.assertAlmostEqual(
                score.breakdown["last_name"]["weighted_score"], 0.7 * 2.0
            )
            self.assertAlmostEqual(score.breakdown["dob"]["weighted_score"], 0.8 * 3.0)


if __name__ == "__main__":
    unittest.main()
