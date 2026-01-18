import json
import glob
from src.database.sql_client import ProductSQLClient
from src.config import OUTPUT_DIR
from src.schema import Product

def main():
    print("===== Starting database loading...")
    client = ProductSQLClient()

    output_files_pattern = str(OUTPUT_DIR / 'batch_*.json')
    files = glob.glob(output_files_pattern)
    print(f"DEBUG: Searching in path: {output_files_pattern}")
    print(f"Found {len(files)} JSON files.")

    total_files = 0

    try:
        for file_path in files:
            batch_data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                for item in raw_data:
                    product = Product(**item)
                    batch_data.append((product, item))

            if batch_data:
                client.bulk_upsert(batch_data)
                total_files += 1

        print(f"DONE. Successfully loaded data from {total_files} files.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()