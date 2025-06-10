import os
import csv
import json
from flask import Flask, render_template, request, jsonify
from matching.matcher import load_data, match_patients, write_match

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_matches_csv(data_dir: str, matches_filename: str, encoding: str) -> None:
    """Create or truncate the matches CSV file and write the header."""
    os.makedirs(data_dir, exist_ok=True)
    matches_csv = os.path.join(data_dir, matches_filename)
    with open(matches_csv, 'w', newline='', encoding=encoding) as f:
        writer = csv.writer(f)
        writer.writerow(['ExternalPatientId', 'InternalPatientId'])

def create_app() -> Flask:
    config = load_config(CONFIG_PATH)
    app = Flask(__name__)

    data_dir = os.path.join(os.path.dirname(__file__), config['DATA_DIR'])
    matches_filename = config['MATCHES_FILENAME']
    encoding = config.get('ENCODING', 'utf-8')
    port = config.get('PORT', 5000)
    debug = config.get('DEBUG', True)

    initialize_matches_csv(data_dir, matches_filename, encoding)

    @app.route('/')
    def index():
        """Render the main page with patient matches."""
        internal, external = load_data(data_dir)
        matches = match_patients(internal, external)
        return render_template('index.html', matches=matches)

    @app.route('/accept', methods=['POST'])
    def accept_match():
        """Accept a match and record it in the matches CSV."""
        data = request.get_json(force=True)
        ext_id = data.get('external_id')
        int_id = data.get('internal_id')
        success = write_match(data_dir, ext_id, int_id)
        return jsonify(success=success), 200 if success else 400

    # Attach config values for use in __main__
    app.config['PORT'] = port
    app.config['DEBUG'] = debug
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'])