from dataclasses import dataclass
from app.matching.normalization import normalize_string
from app.matching.constants import PRECOMPUTED_NORMALIZATION_FIELDS


@dataclass
class Patient:
    """
    Data class representing a patient.

    Attributes:
        patient_id (str): Unique identifier for the patient.
        first_name (str): Patient's first name.
        last_name (str): Patient's last name.
        dob (str): Date of birth of the patient (format: YYYY-MM-DD).
        sex (str): Sex of the patient.
        phone_number (str): Patient's contact phone number.
        address (str): Patient's street address.
        city (str): City of residence.
        zipcode (str): Postal code of the patient's address.
        score (float): Similarity score for matching (default is 0.0).
    """

    patient_id: str
    first_name: str
    last_name: str
    dob: str
    sex: str
    phone_number: str
    address: str
    city: str
    zipcode: str
    score: float = 0.0

    def normalize_fields(self):
        """Attach normalized fields as attributes to this Patient."""
        for field, norm_field in PRECOMPUTED_NORMALIZATION_FIELDS.items():
            setattr(self, norm_field, normalize_string(getattr(self, field, ""), field))
