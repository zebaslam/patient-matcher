"""Data loading and writing functions for patient matching."""

import csv
from pathlib import Path
from typing import Union, List, Dict, Any, Tuple
from app.config import ENCODING, INTERNAL_CSV_PATH, EXTERNAL_CSV_PATH, MATCHES_CSV_PATH


def load_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load CSV file and return list of dictionaries."""
    try:
        with open(file_path, newline="", encoding=ENCODING) as f:
            data = list(csv.DictReader(f))
            print(f"Loaded {len(data)} records from {file_path}")
            return data
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return []
    except (csv.Error, OSError) as e:
        print(f"CSV/OS error loading {file_path}: {e}")
        return []


def load_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load internal and external patient data from CSV files."""
    internal = load_csv(INTERNAL_CSV_PATH)
    external = load_csv(EXTERNAL_CSV_PATH)
    return internal, external


def write_match(external_id: str, internal_id: str) -> bool:
    """Write a match to the matches CSV file."""
    try:
        with open(MATCHES_CSV_PATH, "a", newline="", encoding=ENCODING) as f:
            writer = csv.writer(f)
            writer.writerow([external_id, internal_id])
        return True
    except (OSError, csv.Error) as e:
        print(f"Error writing match: {e}")
        return False
