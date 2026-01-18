from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.database.orm.connector import engine, SessionLocal
from src.database.orm.models import Base, ProductORM
from datetime import datetime, timezone
from sqlalchemy import func

class PostgresORMClient:
    def __init__(self):
        # Create table if not exists
        Base.metadata.create_all(engine)

    def bulk_upsert(self, data: list[dict]):
        if not data:
            return

        # Prepare statements
        utc_now = datetime.now(timezone.utc)
        for item in data:
            if 'created_at' not in item:
                item['created_at'] = utc_now
            item['updated_at'] = utc_now

        stmt = pg_insert(ProductORM).values(data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['id'], # if id is duplicated
            set_={
                "name": stmt.excluded.name,
                "price": stmt.excluded.price,
                "url_key": stmt.excluded.url_key,
                "image_urls": stmt.excluded.image_urls,
                "raw_data": stmt.excluded.raw_data,
                "updated_at": stmt.excluded.updated_at
            }
        )

        # Get connection from pool & exec
        with SessionLocal() as session:
            session.execute(stmt)
            session.commit()
            print(f"[ORM] Saved {len(data)} items.")
