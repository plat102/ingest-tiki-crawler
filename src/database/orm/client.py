from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.database.orm.connector import engine, SessionLocal
from src.database.orm.models import Base, ProductORM

class PostgresORMClient:
    def __init__(self):
        # Create table if not exists
        Base.metadata.create_all(engine)

    def bulk_upsert(self, data: list[dict]):
        if not data:
            return

        # Prepare statements
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
