import sys
import os
import asyncio

# Setup src path as root package
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src import config
from src import utils
from src import crawler

def run():
    print(f"Running with Config:")
    config.print_config()

    product_ids = utils.load_product_ids_from_csv(config.INPUT_FILE)

    # Run crawler
    try:
        asyncio.run(crawler.fetch_all_products(product_ids))
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run()
