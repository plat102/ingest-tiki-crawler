import logging

import psycopg2
from psycopg2 import OperationalError, InterfaceError
from src.database.config import DB_CONFIG_DICT
from src.database.exceptions import (
    DBConnectionError,
    DatabaseError
)

logger = logging.getLogger(__name__)

def get_connection():
    """
    Create a connection to the PostgreSQL database
    TODO: Connection Pool ?
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG_DICT)
        return conn
    except (InterfaceError, OperationalError) as e:
        logger.exception(f'Connection failed: {e}')
        raise DBConnectionError('Could not connect to PostgreSQL database', original_exception=e)
    except Exception as e:
        logger.error(f'Unexpected DB error: {e}')
        raise DatabaseError('Unexpected error', original_exception=e)
