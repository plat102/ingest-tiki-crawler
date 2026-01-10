from pathlib import Path

# API settings
API_URL = 'https://api.tiki.vn'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}

# Batch settings
# TODO

# File paths
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = f"{BASE_DIR}/data/test.csv"
OUTPUT_DIR = f"{BASE_DIR}/data/products"
ERROR_FILE = f"{BASE_DIR}/data/errors.json"
CHECKPOINT_FILE = f"{BASE_DIR}/data/checkpoint.json"

print(INPUT_FILE)
