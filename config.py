import json
import os
from typing import Dict, Any

_config_path = os.path.join(os.path.dirname(__file__), 'config.json')

with open(_config_path, 'r', encoding='utf-8') as f:
    CONFIG: Dict[str, Any] = json.load(f)

# Base config values
DATA_DIR = CONFIG['DATA_DIR']
ENCODING = CONFIG.get('ENCODING', 'utf-8')
DEBUG = CONFIG.get('DEBUG', True)
PORT = CONFIG.get('PORT', 5000)

# Helper to get full file paths
def get_file_path(relative_path: str) -> str:
    """Get full path for a file relative to project root."""
    return os.path.join(os.path.dirname(__file__), relative_path)

# Full file paths
INTERNAL_CSV_PATH = get_file_path(CONFIG['FILES']['INTERNAL_CSV'])
EXTERNAL_CSV_PATH = get_file_path(CONFIG['FILES']['EXTERNAL_CSV'])
MATCHES_CSV_PATH = get_file_path(CONFIG['FILES']['MATCHES_CSV'])