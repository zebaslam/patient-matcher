"""Data loading functions for patient matching."""
import csv
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Tuple
from app.config import ENCODING, INTERNAL_CSV_PATH, EXTERNAL_CSV_PATH

def load_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load CSV file and return list of dictionaries."""
    try:
        with open(file_path, newline='', encoding=ENCODING) as f:
            data = list(csv.DictReader(f))
            print(f"Loaded {len(data)} records from {file_path}")
            return data
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return []
    except Exception as e:
        print(f"Error loading CSV {file_path}: {e}")
        return []

def load_data(data_dir: Optional[Union[str, Path]] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load internal and external patient data from CSV files."""
    internal = load_csv(INTERNAL_CSV_PATH)
    external = load_csv(EXTERNAL_CSV_PATH)
    return internal, external