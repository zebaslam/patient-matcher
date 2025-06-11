import os
import csv
import logging
from flask import Flask, render_template, request, jsonify
from app.matching.matcher import match_patients
from app.matching.data_processor import load_data, write_match
from app.config import ENCODING, DEBUG, PORT, MATCHES_CSV_PATH, LOG_LEVEL
from app.filters import register_filters


def create_app() -> Flask:
    app = Flask(__name__)    
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
    register_filters(app)

    def _init_matches_csv():
        os.makedirs(os.path.dirname(MATCHES_CSV_PATH), exist_ok=True)
        with open(MATCHES_CSV_PATH, 'w', newline='', encoding=ENCODING) as f:
            csv.writer(f).writerow(['ExternalPatientId', 'InternalPatientId'])
    _init_matches_csv()

    @app.route('/')
    def index():
        try:
            internal, external = load_data()
            if not internal or not external:
                return render_template('index.html', matches=[], error="No data found")
            matches = sorted(match_patients(internal, external), key=lambda m: m['score'])
            return render_template('index.html', matches=matches)
        except Exception as e:
            return render_template('index.html', matches=[], error=str(e))

    @app.route('/accept', methods=['POST'])
    def accept_match():
        data = request.get_json(force=True)
        ext_id = data.get('external_id')
        int_id = data.get('internal_id')
        success = write_match(ext_id, int_id)
        return jsonify(success=success), 200 if success else 400

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)