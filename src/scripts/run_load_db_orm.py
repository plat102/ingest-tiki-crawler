import json
import glob
from src.config import OUTPUT_DIR
from src.schema import Product as ProductRawSchema
from src.database.orm.client import PostgresORMClient


def main():
    print("Running minimal ORM load...")
    client = PostgresORMClient()

    files = glob.glob(str(OUTPUT_DIR / "batch_*.json"))

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            if isinstance(raw_data, dict): raw_data = [raw_data]

        batch = []
        for item in raw_data:
            try:
                # 1. Validate (Pydantic)
                p = ProductRawSchema(**item)

                # 2. Convert to dict
                record = p.model_dump()
                record['raw_data'] = item
                batch.append(record)
            except:
                pass

        # 3. Save ORM
        client.bulk_upsert(batch)


if __name__ == "__main__":
    main()
