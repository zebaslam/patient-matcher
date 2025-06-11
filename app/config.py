import json
from pathlib import Path
from typing import Final, Dict, Any

# Load config from JSON file
CONFIG_PATH: Final[Path] = Path(__file__).parent.parent / "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config: Dict[str, Any] = json.load(f)

LOG_LEVEL: Final[str] = config.get("LOG_LEVEL", "WARNING")

# Existing config values
DATA_DIR: Final[str] = config["DATA_DIR"]
ENCODING: Final[str] = config["ENCODING"]
DEBUG: Final[bool] = config["DEBUG"]
PORT: Final[int] = config["PORT"]

# File paths
INTERNAL_CSV_PATH: Final[Path] = Path(DATA_DIR) / config["FILES"]["INTERNAL_CSV"]
EXTERNAL_CSV_PATH: Final[Path] = Path(DATA_DIR) / config["FILES"]["EXTERNAL_CSV"]
MATCHES_CSV_PATH: Final[Path] = Path(DATA_DIR) / config["FILES"]["MATCHES_CSV"]

# Matching configuration
FIELD_WEIGHTS: Final[Dict[str, float]] = config["MATCHING"]["FIELD_WEIGHTS"]
FIELD_TYPES: Final[Dict[str, str]] = config["MATCHING"]["FIELD_TYPES"]
MATCH_THRESHOLD: Final[float] = config["MATCHING"]["MATCH_THRESHOLD"]

# Similarity thresholds
SIMILARITY_THRESHOLDS: Final[Dict[str, float]] = config["MATCHING"][
    "SIMILARITY_THRESHOLDS"
]
FIRST_NAME_MIDDLE_NAME: Final[float] = SIMILARITY_THRESHOLDS["FIRST_NAME_MIDDLE_NAME"]
FIRST_NAME_MATCH: Final[float] = SIMILARITY_THRESHOLDS["FIRST_NAME_MATCH"]
ADDRESS_BASE_MATCH: Final[float] = SIMILARITY_THRESHOLDS["ADDRESS_BASE_MATCH"]
PHONE_PARTIAL_MATCH: Final[float] = SIMILARITY_THRESHOLDS["PHONE_PARTIAL_MATCH"]
PHONE_AREA_CODE_MATCH: Final[float] = SIMILARITY_THRESHOLDS["PHONE_AREA_CODE_MATCH"]
GENERAL_SIMILARITY_MULTIPLIER: Final[float] = SIMILARITY_THRESHOLDS[
    "GENERAL_SIMILARITY_MULTIPLIER"
]
ADDRESS_SIMILARITY_MULTIPLIER: Final[float] = SIMILARITY_THRESHOLDS[
    "ADDRESS_SIMILARITY_MULTIPLIER"
]
