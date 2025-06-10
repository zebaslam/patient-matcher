import json
from pathlib import Path

# Load config from JSON file
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

# Existing config values
DATA_DIR = config["DATA_DIR"]
ENCODING = config["ENCODING"]
DEBUG = config["DEBUG"]
PORT = config["PORT"]

# File paths
INTERNAL_CSV_PATH = Path(DATA_DIR) / config["FILES"]["INTERNAL_CSV"]
EXTERNAL_CSV_PATH = Path(DATA_DIR) / config["FILES"]["EXTERNAL_CSV"]
MATCHES_CSV_PATH = Path(DATA_DIR) / config["FILES"]["MATCHES_CSV"]

# Matching configuration
FIELD_WEIGHTS = config["MATCHING"]["FIELD_WEIGHTS"]
FIELD_TYPES = config["MATCHING"]["FIELD_TYPES"]
MATCH_THRESHOLD = config["MATCHING"]["MATCH_THRESHOLD"]