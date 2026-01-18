import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG_DICT = {
    'dbname': os.getenv('DB_NAME', 'tiki_db'),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "secret"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}
