import logging
from flask import Flask, render_template, request, jsonify
from app.matching.matcher import match_patients
from app.io.csv_io import load_data, write_match, create_output_files, write_all_matches
from app.config import DEBUG, PORT, LOG_LEVEL
from app.filters import register_filters


def create_app() -> Flask:
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
    register_filters(flask_app)

    create_output_files()

    @flask_app.route("/")
    def index():
        """Render the main index page with patient matches."""
        try:
            internal, external = load_data()
            if not internal or not external:
                return render_template("index.html", matches=[], error="No data found")
            matches = sorted(
                match_patients(internal, external), key=lambda m: m["score"]
            )
            write_all_matches(matches)
            return render_template("index.html", matches=matches)
        except (IOError, ValueError) as e:
            return render_template("index.html", matches=[], error=str(e))

    @flask_app.route("/accept", methods=["POST"])
    def accept_match():
        """Accept a patient match and write it to the CSV file."""
        data = request.get_json(force=True)
        ext_id = data.get("external_id")
        int_id = data.get("internal_id")
        success = write_match(ext_id, int_id)
        return jsonify(success=success), 200 if success else 400

    return flask_app


app = create_app()

if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT)
