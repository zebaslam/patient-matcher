# Patient Roster Matching Web Application

This project is a local-only web application that matches patients from two datasets:

- `data/internal.csv` (internal hospital's patient roster)
- `data/external.csv` (external medical practice's roster)

The goal is to identify likely matches based on personal attributes like name, date of birth, address, etc., despite data inconsistencies.

---

## 🛠 Setup Instructions

### Requirements

- Python 3.11
- pip

### Installation

1. Clone the repository and navigate into it:

```bash
git clone https://github.com/zebaslam/patient-matcher.git
cd patient-matcher
```

Alternatively,

Download zip file
Unzip attached zip file from email

2. (Optional) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application locally:

```bash
python main.py
```

5. Open your browser and visit: `http://localhost:5000`

6. Additional files generated include:

- `data/matches.csv` -> showcases all matches
- `data/accepted.csv` -> showcases accepted matches from UI

---

## 🧠 Matching Algorithm Overview

The algorithm uses a **hybrid similarity approach**:

- **Normalization**: All strings are lowercased, punctuation and whitespace are removed, and phone numbers are reduced to digits only.
- **Pre-filtering (Hash-based Indexing)**: To improve performance and avoid poor matches, internal patients are efficiently indexed by normalized
- **Date of Birth** and **Sex**. For each external patient, only internal patients with matching normalized values are considered, enabling fast lookups instead of scanning the entire list.
- **Field-specific similarity**:
  - **First Name**: Compares only the first token of each name using Jaro-Winkler similarity
  - **Last Name**: Jaro-Winkler
  - **Address**: Combined Jaccard + Levenshtein
  - **Phone Number**: Digit-aware phone similarity
  - **Zip Code**, **City**: Edit distance (Levenshtein)
  - **DOB, Sex**: Exact match

Each field is given a **weight** (from `config.json`), and a final score is computed as a weighted average of all field similarities.

A match is accepted if its score exceeds a defined threshold (defined in `config.json`). The best match per external patient is written to `matches.csv`.

---

## 🧹 Data Cleaning and Preprocessing

- All string fields are stripped of punctuation and lowercased.
- Phone numbers are normalized to just digits (e.g., `"(555) 123-4567"` → `"5551234567"`).
- Dates of birth are parsed and formatted as `YYYY-MM-DD`.
- Token-based normalization is used for addresses to improve tolerance to reordering or punctuation differences.

---

## ✅ Assumptions and Simplifications

- **DOB** and **Sex** are reliable and used as hard filters.
- There is **no unique patient ID** shared between files.
- The matching algorithm prioritizes **precision over recall**, meaning it avoids false positives even if that leads to more unmatched rows.
- Only the **best match** per external patient is recorded in `matches.csv`; if no match passes the threshold, that patient is excluded.

---

## 🏥 Data Model Overview

The application uses Python `@dataclass` models to represent core entities:

- **Patient**: patient_id, first_name, last_name, dob, sex, phone_number, address, city, zipcode, score
- **MatchScore**: value, breakdown, threshold, meets_threshold, reason
- **MatchOutput**: external_id, internal_id
- **FieldSimilarityResult**: similarity, algorithm
- **BestMatch**: internal (Patient), score (MatchScore)
- **MatchResult**: external (Patient), internal (Patient), score (MatchScore)

---

## 🧪 Running Tests

To run the test suite using Python's built-in `unittest` framework:

```bash
python -m unittest discover tests
```

This will run all unit tests in the `tests/` directory.

---
