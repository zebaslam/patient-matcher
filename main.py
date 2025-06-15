import logging
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify
from app.matching.matcher import match_patients
from app.io.csv_io import load_data, write_match, create_output_files, write_all_matches
from app.config import DEBUG, PORT, LOG_LEVEL
from app.filters import register_filters
from app.models.match_output import MatchOutput


PATIENT_FIELDS = [
    "patient_id",
    "first_name",
    "last_name",
    "dob",
    "sex",
    "phone_number",
    "address",
    "city",
    "zipcode",
]


def create_app() -> Flask:
    """Create and configure the Flask application."""
    flask_app = Flask(__name__, template_folder="app/templates")
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
    register_filters(flask_app)

    create_output_files()

    @flask_app.route("/")
    def index():
        """Render the main index page with patient matches."""
        try:
            internal, external = load_data()
            if not internal or not external:
                return render_template(
                    "index.html",
                    matches=[],
                    error="No data found",
                    patient_fields=PATIENT_FIELDS,
                )
            matches = sorted(
                match_patients(internal, external),
                key=lambda m: m.score,
                reverse=False,
            )
            write_all_matches(matches)
            return render_template(
                "index.html", matches=matches, patient_fields=PATIENT_FIELDS
            )
        except (IOError, ValueError) as e:
            return render_template("index.html", matches=[], error=str(e))

    @flask_app.route("/accept", methods=["POST"])
    def accept_match():
        """Accept a patient match and write it to the CSV file."""
        data = request.get_json(force=True)
        match_output = MatchOutput(
            external_id=data.get("external_id"),
            internal_id=data.get("internal_id"),
        )
        success = write_match(match_output)
        return jsonify(success=success), (200 if success else 400)

    return flask_app


app = create_app()


def open_browser():
    """Open the default web browser to the application's home page."""
    webbrowser.open(f"http://127.0.0.1:{PORT}/")


if __name__ == "__main__":
    import os

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.0, open_browser).start()
    app.run(debug=DEBUG, port=PORT)
