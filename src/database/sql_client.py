import json
import psycopg2
from psycopg2.extras import  execute_values
from pygments.lexers import data

from src.database.connect import get_connection

class ProductSQLClient:
    def __init__(self):
        self.conn = get_connection()
        # Create table when init
        self._create_table()

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
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """

        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()

    def bulk_upsert(self, data: list[dict]):
        if not data:
            return
        query = """
            INSERT INTO products (
                id, name, url_key, price, description, 
                image_urls, raw_data
            )
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                url_key = EXCLUDED.url_key,
                price = EXCLUDED.price,
                description = EXCLUDED.description,
                image_urls = EXCLUDED.image_urls,
                raw_data = EXCLUDED.raw_data,
                updated_at = NOW(); -- updated timestamp
            """

        # Match data with db schema
        values = []
        for product in data:
            record = (
                product.get("id"),
                product.get("name"),
                product.get("url_key"),
                product.get("price"),
                product.get("description"),
                json.dumps(product.get("image_urls", [])),
                json.dumps(product)
            )
            values.append(record)

        # Exec upsert
        try:
            with self.conn.cursor() as cur:
                execute_values(cur, query, values)
                self.conn.commit()
                print(f" [PostgreSQL client] Loaded batch of {len(data)} products")
        except Exception as e:
            self.conn.rollback()
            print(f" [PostgreSQL client] Error: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
