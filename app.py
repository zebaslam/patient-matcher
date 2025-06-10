from flask import Flask, render_template, request, jsonify
from matching.matcher import load_data, match_patients, write_match
import os
import csv
import json

# Load config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)
    
app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), config['DATA_DIR'])
MATCHES_FILENAME = config['MATCHES_FILENAME']
MATCHES_CSV = os.path.join(DATA_DIR, MATCHES_FILENAME)
ENCODING = config.get('ENCODING', 'utf-8')

def initialize_matches_csv() -> None:
    """Create or truncate the matches CSV file and write the header."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MATCHES_CSV, 'w', newline='', encoding=ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(['ExternalPatientId', 'InternalPatientId'])

initialize_matches_csv()

@app.route('/')
def index():
    """Render the main page with patient matches."""
    internal, external = load_data(DATA_DIR)
    matches = match_patients(internal, external)
    return render_template('index.html', matches=matches)

@app.route('/accept', methods=['POST'])
def accept_match():
    """Accept a match and record it in the matches CSV."""
    data = request.get_json(force=True)
    ext_id = data.get('external_id')
    int_id = data.get('internal_id')
    success = write_match(DATA_DIR, ext_id, int_id)
    return jsonify(success=success), 200 if success else 400

if __name__ == '__main__':
    app.run(debug=True)