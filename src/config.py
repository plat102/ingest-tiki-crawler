from pathlib import Path

# ----- API settings -----
API_URL = 'https://api.tiki.vn/product-detail/api/v1/products'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}

# ----- Concurrency settings -----
MAX_CONCURRENT_TASKS = 30 # max task running (n of fetch product running)
BATCH_SIZE = 1000 # products/JSON
DELAY_AFTER_BATCH = 0.5
REQUEST_RANDOM_SLEEP_MIN=0.2
REQUEST_RANDOM_SLEEP_MAX=0.5

# ----- Requests settings -----
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# ----- File paths -----
BASE_DIR = Path(__file__).parent.parent
# INPUT_FILE = f"{BASE_DIR}/data/test.csv"
INPUT_FILE = f"{BASE_DIR}/data/products-0-200000.csv"
OUTPUT_DIR = f"{BASE_DIR}/data/products"
ERROR_FILE = f"{BASE_DIR}/data/errors.jsonl"
CHECKPOINT_FILE = f"{BASE_DIR}/data/checkpoint.json"

print(INPUT_FILE)
