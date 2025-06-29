import unittest
from unittest.mock import patch
from main import PATIENT_FIELDS, app
from app.models.match_result import MatchResult
from app.models.patient import Patient
from app.models.match_score import MatchScore


class TestMain(unittest.TestCase):
    """
    Unit tests for the main application routes and functionality.

    This class tests the behavior of the Flask application defined in `main.py`.
    It includes tests for the index route under various conditions, such as when
    there is no data, when matches are found, and when exceptions occur during data loading.
    """

    def setUp(self):
        """
        Set up the test client and configure the application for testing.

        This method initializes the Flask test client and sets the application
        configuration to enable testing mode.
        """
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("main.load_data")
    @patch("main.render_template")
    def test_index_no_data(self, mock_render_template, mock_load_data):
        """
        Test the index route when no data is available.

        This test verifies that the index route handles the case where no data
        is loaded and renders the appropriate template with an error message.
        """
        mock_load_data.return_value = ([], [])
        mock_render_template.return_value = "no data"
        response = self.client.get("/")
        mock_render_template.assert_called_with(
            "index.html",
            matches=[],
            error="No data found",
            patient_fields=PATIENT_FIELDS,
        )
        self.assertEqual(response.data, b"no data")

    @patch("main.load_data")
    @patch("main.match_patients")
    @patch("main.write_all_matches")
    @patch("main.render_template")
    def test_index_with_matches(
        self,
        mock_render_template,
        mock_write_all_matches,
        mock_match_patients,
        mock_load_data,
    ):
        """
        Test the index route when matches are found and rendered.

        This test verifies that the index route correctly loads data, matches patients,
        sorts the matches, writes them to a file, and renders the appropriate template.
        """
        internal = [{"patient_id": 1}]
        external = [{"patient_id": 2}]
        dummy_patient = Patient(
            patient_id="dummy",
            first_name="",
            last_name="",
            dob="",
            sex="",
            phone_number="",
            address="",
            city="",
            zipcode="",
        )
        matches = [
            MatchResult(
                external=dummy_patient,
                internal=dummy_patient,
                score=MatchScore(value=2, breakdown={}),
            ),
            MatchResult(
                external=dummy_patient,
                internal=dummy_patient,
                score=MatchScore(value=1, breakdown={}),
            ),
        ]
        mock_load_data.return_value = (internal, external)
        mock_match_patients.return_value = matches
        mock_render_template.return_value = "matches rendered"
        response = self.client.get("/")
        sorted_matches = sorted(matches, key=lambda m: m.score.value)
        mock_render_template.assert_called_with(
            "index.html", matches=sorted_matches, patient_fields=PATIENT_FIELDS
        )
        mock_write_all_matches.assert_called_with(sorted_matches)
        self.assertEqual(response.data, b"matches rendered")

    @patch("main.load_data", side_effect=IOError("file error"))
    @patch("main.render_template")
    def test_index_ioerror(
        self, mock_render_template, mock_load_data
    ):  # pylint: disable=unused-argument
        """
        Test the index route when an IOError occurs during data loading.

        This test verifies that the index route handles IOError exceptions gracefully
        and renders the appropriate template with an error message.
        """
        mock_render_template.return_value = "error page"
        response = self.client.get("/")
        mock_render_template.assert_called_with(
            "index.html", matches=[], error="file error"
        )
        self.assertEqual(response.data, b"error page")

    @patch("main.load_data", side_effect=ValueError("bad value"))
    @patch("main.render_template")
    def test_index_valueerror(
        self, mock_render_template, mock_load_data
    ):  # pylint: disable=unused-argument
        """
        Test the index route when a ValueError occurs during data loading.

        This test verifies that the index route handles ValueError exceptions gracefully
        and renders the appropriate template with an error message.
        """
        mock_render_template.return_value = "error page"
        response = self.client.get("/")
        mock_render_template.assert_called_with(
            "index.html", matches=[], error="bad value"
        )
        self.assertEqual(response.data, b"error page")

    @patch("main.write_match")
    @patch("main.MatchOutput")
    def test_accept_match_success(self, mock_match_output, mock_write_match):
        """
        Test the accept_match route when writing the match is successful.

        This test verifies that the accept_match route processes the POSTed JSON,
        creates a MatchOutput, writes the match, and returns a success response.
        """
        mock_write_match.return_value = True
        mock_match_output.return_value = "mocked_output"
        data = {"external_id": "ext123", "internal_id": "int456"}
        response = self.client.post(
            "/accept",
            json=data,
        )
        mock_match_output.assert_called_with(external_id="ext123", internal_id="int456")
        mock_write_match.assert_called_with("mocked_output")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})

    @patch("main.write_match")
    @patch("main.MatchOutput")
    def test_accept_match_failure(self, mock_match_output, mock_write_match):
        """
        Test the accept_match route when writing the match fails.

        This test verifies that the accept_match route returns a 400 response
        when write_match returns False.
        """
        mock_write_match.return_value = False
        mock_match_output.return_value = "mocked_output"
        data = {"external_id": "ext123", "internal_id": "int456"}
        response = self.client.post(
            "/accept",
            json=data,
        )
        mock_match_output.assert_called_with(external_id="ext123", internal_id="int456")
        mock_write_match.assert_called_with("mocked_output")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"success": False})


if __name__ == "__main__":
    unittest.main()
