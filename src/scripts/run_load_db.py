import logging
import json
import glob
import sys
import time
from src.database.sql_client import ProductSQLClient
from src.database.exceptions import DBConnectionError
from src.config import OUTPUT_DIR
from src.schema import Product
from src.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def main():
    logger.info("===== Starting database loading...")
    client = None
    max_retries = 3
    # Connect
    for attempt in range(max_retries):
        try:
            client = ProductSQLClient()
            logger.info('Database client established.')
        except DBConnectionError:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection error. Retrying {attempt/max_retries} in 5 seconds.")
                time.sleep(5)
            else:
                logger.exception('Failed to connect to database.')
        except Exception as e:
            logger.error(f'Unexpected error during conn init: {e}')
    if not client:
        logger.error('Connection failed. Aborting.')
        sys.exit(1)

    # Read data files
    output_files_pattern = str(OUTPUT_DIR / 'batch_*.json')
    files = glob.glob(output_files_pattern)
    logger.info(f"Found {len(files)} files.")

    total_files = 0

    try:
        for file_path in files:
            batch_data = []
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    for item in raw_data:
                        product = Product(**item)
                        batch_data.append((product, item))

                if batch_data:
                    client.bulk_upsert(batch_data)
                    total_files += 1
            except Exception as e:
                logger.error(f"Error when process file {file_path} : {e}")

        logger.info(f"DONE. Successfully loaded data from {total_files} files.")

    except Exception as e:
        logger.error(f"Error in db load script: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()