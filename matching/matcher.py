import csv
import os
from pathlib import Path
from typing import Union, List, Dict, Any, Tuple
from config import ENCODING, INTERNAL_CSV_PATH, EXTERNAL_CSV_PATH, MATCHES_CSV_PATH

def load_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load CSV file and return list of dictionaries."""
    with open(file_path, newline='', encoding=ENCODING) as f:
        return list(csv.DictReader(f))

def load_data(data_dir: Union[str, Path] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load internal and external patient data from CSV files."""
    internal = load_csv(INTERNAL_CSV_PATH)
    external = load_csv(EXTERNAL_CSV_PATH)
    return internal, external

def match_patients(internal: List[Dict[str, Any]], external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match patients between internal and external lists."""
    matches = []

    # Inject stable unique IDs
    _add_unique_ids(internal, 'int')
    _add_unique_ids(external, 'ext')

    # Stub match: naive 1-to-1 pairing for demo/testing
    for e_idx, e in enumerate(external):
        if e_idx < len(internal):
            matches.append({
                'external': e,
                'internal': internal[e_idx],
                'score': 1.0  # placeholder score
            })

    return matches

def write_match(external_id: str, internal_id: str) -> bool:
    """Write a match to the matches CSV file."""
    try:
        with open(MATCHES_CSV_PATH, 'a', newline='', encoding=ENCODING) as f:
            writer = csv.writer(f)
            writer.writerow([external_id, internal_id])
        return True
    except Exception as e:
        print(f"Error writing match: {e}")
        return False

def _add_unique_ids(patients: List[Dict[str, Any]], prefix: str) -> None:
    """Internal helper to add stable unique IDs to patient records."""
    for i, patient in enumerate(patients):
        patient['Id'] = f'{prefix}-{i}'