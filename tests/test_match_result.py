"""
Unit tests for the MatchResult model and its integration with BestMatch, Patient, and MatchScore.
"""

import unittest
from app.models.match_result import MatchResult
from app.models.patient import Patient
from app.models.best_match import BestMatch
from app.models.match_score import MatchScore


class DummyPatient(Patient):
    """A minimal Patient subclass for testing purposes."""

    def __init__(self, patient_id):
        super().__init__(
            patient_id=patient_id,
            first_name="Test",
            last_name="User",
            dob="2000-01-01",
            sex="U",
            phone_number="0000000000",
            address="123 Test St",
            city="Testville",
            zipcode="00000",
        )
        self.id = patient_id


class DummyMatchScore(MatchScore):
    """A minimal MatchScore subclass for testing purposes."""

    def __init__(self, value):
        super().__init__(value=value, breakdown={})
        self.value = value


def make_patient(patient_id="external"):
    """Create a dummy external patient for testing."""
    return DummyPatient(patient_id=patient_id)


def make_internal_patient(patient_id="internal"):
    """Create a dummy internal patient for testing."""
    return DummyPatient(patient_id=patient_id)


def make_match_score(value=0.95):
    """Create a dummy match score for testing."""
    return DummyMatchScore(value=value)


def make_best_match(internal=None, score=None):
    """Create a BestMatch object for testing."""
    if score is None:
        score = make_match_score()
    return BestMatch(internal=internal, score=score)


class TestMatchResult(unittest.TestCase):
    """Unit tests for the MatchResult.from_best_match method."""

    def test_from_best_match_success(self):
        """Test that from_best_match returns a MatchResult with correct fields when internal is present."""
        external = make_patient("external-1")
        internal = make_internal_patient("internal-1")
        score = make_match_score(0.88)
        best_match = make_best_match(internal=internal, score=score)

        result = MatchResult.from_best_match(external, best_match)

        self.assertEqual(result.external, external)
        self.assertEqual(result.internal, internal)
        self.assertEqual(result.score, score)

    def test_from_best_match_raises_when_internal_none(self):
        """Test that from_best_match raises ValueError if BestMatch.internal is None."""
        external = make_patient("external-2")
        score = make_match_score(0.77)
        best_match = make_best_match(internal=None, score=score)

        with self.assertRaises(ValueError) as excinfo:
            MatchResult.from_best_match(external, best_match)
        self.assertIn("BestMatch.internal cannot be None", str(excinfo.exception))


if __name__ == "__main__":
    unittest.main()
