import os
import csv
from flask import Flask, render_template, request, jsonify
from app.matching.matcher import match_patients, write_match
from app.matching.data_loader import load_data
from app.config import ENCODING, DEBUG, PORT, MATCHES_CSV_PATH
from app.filters import register_filters

def initialize_matches_csv() -> None:
    """Create or truncate the matches CSV file and write the header."""
    # Extract directory from the full path
    matches_dir = os.path.dirname(MATCHES_CSV_PATH)
    os.makedirs(matches_dir, exist_ok=True)
    
    with open(MATCHES_CSV_PATH, 'w', newline='', encoding=ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(['ExternalPatientId', 'InternalPatientId'])

def create_app() -> Flask:
    app = Flask(__name__)
    
    register_filters(app)
    initialize_matches_csv()

    @app.route('/')
    def index():
        """Render the main page with patient matches."""
        try:
            print("Loading data...")
            internal, external = load_data()
            print(f"Loaded: Internal={len(internal)}, External={len(external)}")
            
            if not internal or not external:
                print("Warning: No data loaded!")
                return render_template('index.html', matches=[], error="No data found")
            
            print("Running matching algorithm...")
            matches = match_patients(internal, external)
            print(f"Found {len(matches)} matches")
            
            return render_template('index.html', matches=matches)
            
        except Exception as e:
            print(f"Error in index route: {e}")
            import traceback
            traceback.print_exc()
            return render_template('index.html', matches=[], error=str(e))

    @app.route('/accept', methods=['POST'])
    def accept_match():
        """Accept a match and record it in the matches CSV."""
        data = request.get_json(force=True)
        
        # Use the actual patient IDs from the data
        ext_id = data.get('external_id')  # This should be the real ExternalPatientId
        int_id = data.get('internal_id')  # This should be the real InternalPatientId
        
        success = write_match(ext_id, int_id)
        return jsonify(success=success), 200 if success else 400

    # Attach config values for use in __main__
    app.config['PORT'] = PORT
    app.config['DEBUG'] = DEBUG
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)