from flask import Flask, render_template, request, redirect, url_for, jsonify
from matching.matcher import *
import os
import csv

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MATCHES_CSV = os.path.join(DATA_DIR, 'matches.csv')

# Truncate matches.csv on startup
with open(MATCHES_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ExternalPatientId', 'InternalPatientId'])


@app.route('/')
def index():
    internal, external = load_data(DATA_DIR)
    matches = match_patients(internal, external)
    return render_template('index.html', matches=matches)


@app.route('/accept', methods=['POST'])
def accept_match():
    data = request.get_json(force=True)
    print("JSON received:", data)
    ext_id = data.get('external_id')
    int_id = data.get('internal_id')
    print(f"Received Accept: external_id={ext_id}, internal_id={int_id}")
    success = write_match(DATA_DIR, ext_id, int_id)
    return jsonify(success=success), 200 if success else 400

if __name__ == '__main__':
    app.run(debug=True)