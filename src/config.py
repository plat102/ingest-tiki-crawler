from pathlib import Path

# ----- API settings -----
API_URL = 'https://api.tiki.vn/product-detail/api/v1/products'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}

# ----- Concurrency settings -----
MAX_CONCURRENT_TASKS = 50 # max task running (n of fetch product running)
BATCH_SIZE = 100 # products/JSON

# ----- Requests settings -----
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# ----- File paths -----
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = f"{BASE_DIR}/data/test.csv"
OUTPUT_DIR = f"{BASE_DIR}/data/products"
ERROR_FILE = f"{BASE_DIR}/data/errors.json"
CHECKPOINT_FILE = f"{BASE_DIR}/data/checkpoint.json"

print(INPUT_FILE)
