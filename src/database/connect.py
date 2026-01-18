import psycopg2
from src.database.config import DB_CONFIG_DICT

def get_connection():
    """
    Create a connection to the PostgreSQL database
    TODO: Connection Pool ?
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG_DICT)
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        raise e
