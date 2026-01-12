import sys
import os
import asyncio
import argparse

# Setup src path as root package
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

def run():
    # Parse entry args & setup env
    parser = argparse.ArgumentParser('Tiki product crawler')
    parser.add_argument('--env', default=".env", help='.env file')
    args = parser.parse_args()
    os.environ['TIKI_CRAWL_ENV_FILE'] = args.env

    from src import config
    from src import utils
    from src import crawler

    # Check config & load raw ids
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
