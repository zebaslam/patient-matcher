"""Data loading and writing functions for patient matching."""

import logging as log
import csv
import os
from pathlib import Path
from typing import Union, List, Tuple
from app.config import (
    ENCODING,
    INTERNAL_CSV_PATH,
    EXTERNAL_CSV_PATH,
    MATCHES_CSV_PATH,
    ACCEPTED_CSV_PATH,
)
from app.models.patient import Patient


OUTPUT_HEADER = ["ExternalPatientId", "InternalPatientId"]


def load_patients(file_path: Union[str, Path], id_col: str) -> List[Patient]:
    """Load CSV file and return list of Patient objects."""
    try:
        with open(file_path, newline="", encoding=ENCODING) as f:
            reader = csv.DictReader(f)
            return [
                Patient(
                    patient_id=row[id_col],
                    first_name=row["FirstName"],
                    last_name=row["LastName"],
                    dob=row["DOB"],
                    sex=row["Sex"],
                    phone_number=row["PhoneNumber"],
                    address=row["Address"],
                    city=row["City"],
                    zipcode=row["ZipCode"],
                )
                for row in reader
            ]
    except IOError as e:
        log.error("Error loading %s: %s", file_path, e)
        return []


def load_data() -> Tuple[List[Patient], List[Patient]]:
    """Load internal and external patient data as Patient objects."""
    internal = load_patients(INTERNAL_CSV_PATH, "InternalPatientId")
    external = load_patients(EXTERNAL_CSV_PATH, "ExternalPatientId")
    return internal, external


def write_match(external_id: str, internal_id: str) -> bool:
    """Write an accepted match to the accepted CSV file."""
    try:
        with open(ACCEPTED_CSV_PATH, "a", newline="", encoding=ENCODING) as f:
            csv.writer(f).writerow([external_id, internal_id])
        return True
    except ValueError as e:
        log.error("Error writing match: %s", e)
        return False


def create_output_files():
    """Create (overwrite) matches and accepted CSV files with headers."""
    os.makedirs(MATCHES_CSV_PATH.parent, exist_ok=True)
    os.makedirs(ACCEPTED_CSV_PATH.parent, exist_ok=True)
    for path in [MATCHES_CSV_PATH, ACCEPTED_CSV_PATH]:
        with open(path, "w", newline="", encoding=ENCODING) as f:
            csv.writer(f).writerow(OUTPUT_HEADER)


def write_all_matches(matches: list):
    """Overwrite matches.csv with all matches (no scores)."""
    with open(MATCHES_CSV_PATH, "w", newline="", encoding=ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_HEADER)
        for m in matches:
            writer.writerow(
                [
                    m["external"].patient_id,
                    m["internal"].patient_id,
                ]
            )
