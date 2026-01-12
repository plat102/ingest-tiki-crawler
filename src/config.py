import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def get_env_str(key: str, default: str) -> str:
    return os.getenv(key, default)

def get_env_int(key: str, default: int) -> int:
    try:
        value = os.getenv(key)
        return int(value) if value is not None else default
    except ValueError:
        print(f"Config Warning: '{key}' must be integer. Using default: {default}")
        return default

def get_env_float(key: str, default: float) -> float:
    try:
        value = os.getenv(key)
        return float(value) if value is not None else default
    except ValueError:
        print(f"Config Warning: '{key}' must be float. Using default: {default}")
        return default

# ----- Paths Settings -----
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILENAME = get_env_str("INPUT_FILENAME", "test.csv")
INPUT_FILE = DATA_DIR / INPUT_FILENAME

OUTPUT_DIR = DATA_DIR / "products"
ERROR_FILE = DATA_DIR / "errors.jsonl"
CHECKPOINT_FILE = DATA_DIR / "checkpoint.json"

# ----- API Settings -----
API_URL = get_env_str('API_URL', 'https://api.tiki.vn/product-detail/api/v1/products')

DEFAULT_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
HEADERS = {
    'User-Agent': get_env_str('USER_AGENT', DEFAULT_UA)
}

# ----- Concurrency Settings -----
MAX_CONCURRENT_TASKS = get_env_int('MAX_CONCURRENT_TASKS', 30)
BATCH_SIZE = get_env_int('BATCH_SIZE', 1000)
DELAY_AFTER_BATCH = get_env_float('DELAY_AFTER_BATCH', 0.5)
REQUEST_RANDOM_SLEEP_MIN = get_env_float('REQUEST_RANDOM_SLEEP_MIN', 0.2)
REQUEST_RANDOM_SLEEP_MAX = get_env_float('REQUEST_RANDOM_SLEEP_MAX', 0.5)

# ----- Requests Settings -----
TIMEOUT = get_env_int('TIMEOUT', 30)
MAX_RETRIES = get_env_int('MAX_RETRIES', 3)
RETRY_DELAY = get_env_int('RETRY_DELAY', 2)

# ----- Config print when imported -----
def print_config():
    print(f"{'='*40}")
    print(f"CONFIG LOADED")
    print(f"\tInput:       {INPUT_FILENAME}")
    print(f"\tConcurrency: {MAX_CONCURRENT_TASKS}")
    print(f"\tBatch Size:  {BATCH_SIZE}")
    print()
