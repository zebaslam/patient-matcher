import json
import os
from typing import Dict, Any

# Look for config.json in the parent directory (project root)
_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

with open(_config_path, 'r', encoding='utf-8') as f:
    CONFIG: Dict[str, Any] = json.load(f)

# Base config values
DATA_DIR = CONFIG['DATA_DIR']
ENCODING = CONFIG.get('ENCODING', 'utf-8')
DEBUG = CONFIG.get('DEBUG', True)
PORT = CONFIG.get('PORT', 5000)

# Build paths using DATA_DIR + filename from config
INTERNAL_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), DATA_DIR, CONFIG['FILES']['INTERNAL_CSV'])
EXTERNAL_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), DATA_DIR, CONFIG['FILES']['EXTERNAL_CSV'])
MATCHES_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), DATA_DIR, CONFIG['FILES']['MATCHES_CSV'])