import logging
import json
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import  execute_values
from psycopg2 import OperationalError, InterfaceError, IntegrityError

from src.database.config import DB_CONFIG_DICT
from src.schema import Product
from src.database.connect import get_connection
from src.database.exceptions import (
    DBConnectionError,
    DBConstraintError,
    DBOperationError,
    DatabaseError
)

logger = logging.getLogger(__name__)

class ProductSQLClient:
    def __init__(self):
        self.conn =  None
        self.connect()
        # Create table when init
        self._create_table()

    def connect(self):
        """ Create a connection to the PostgreSQL database
        TODO: Connection Pool ?
        """
        try:
            self.conn = psycopg2.connect(**DB_CONFIG_DICT)
            logger.debug(f"[PostgreSQL client] Connected to database")
        except (InterfaceError, OperationalError) as e:
            logger.exception('Connection failed')
            raise DBConnectionError('Could not connect to PostgreSQL database', original_exception=e)
        except Exception as e:
            logger.error(f'Unexpected DB error: {e}')
            raise DatabaseError('Unexpected error', original_exception=e)

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id BIGINT PRIMARY KEY,
            name TEXT NOT NULL,
            url_key TEXT NOT NULL,
            price DECIMAL(12,2) NOT NULL,
            description TEXT,
            image_urls JSONB,
            raw_data JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """

        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logger.error(f" Failed to init table: {e}")
            raise DBOperationError('Failed to init table', original_exception=e)

    def _map_product_to_tuple(self, product: Product, raw_dict: dict) -> tuple:
        """Convert Product (crawled) to tuple for db insert"""
        return (
            product.id,
            product.name,
            product.url_key,
            product.price,
            product.description,
            json.dumps(product.image_urls),
            json.dumps(raw_dict)
        )

    def bulk_upsert(self, data: list[tuple[Product, dict]]) :
        if not data:
            return
        utc_now = datetime.now(timezone.utc).isoformat()
        query = """
            INSERT INTO products (
                id, name, url_key, price, description, 
                image_urls, raw_data,
                created_at, updated_at
            )
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                url_key = EXCLUDED.url_key,
                price = EXCLUDED.price,
                description = EXCLUDED.description,
                image_urls = EXCLUDED.image_urls,
                raw_data = EXCLUDED.raw_data,
                updated_at = EXCLUDED.updated_at;
            """

        # Match data with db schema
        values = []
        for item in data:
            record = self._map_product_to_tuple(product=item[0], raw_dict=item[1])
            full_record = record + (utc_now, utc_now)
            values.append(full_record)

        # Exec upsert
        try:
            with self.conn.cursor() as cur:
                execute_values(cur, query, values)
                self.conn.commit()
                logger.info(f" [PostgreSQL client] At {utc_now} - Loaded batch of {len(data)} products")

        except IntegrityError as e:
            self.conn.rollback()
            logger.error(f'Data integrity error: {e}')
            raise DBConstraintError('Data constraint violated', original_exception=e)

        except (OperationalError, IntegrityError) as e:
            self.conn.rollback()
            logger.error(f'Connection lost during upsert: {e}')
            raise DBConnectionError('Connection error', original_exception=e)

        except Exception as e:
            self.conn.rollback()
            logger.error(f"DB Error: {e}")
            raise DatabaseError("Unexpected upsert failed", original_exception=e)

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info('Database connection closed')
