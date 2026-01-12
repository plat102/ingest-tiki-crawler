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
    parser.add_argument('--retry-error', action='store_true', help='Retry failed IDs from error log')

    args = parser.parse_args()
    os.environ['TIKI_CRAWL_ENV_FILE'] = args.env

    from src import config
    from src import utils
    from src import crawler

    # Check config & load raw ids
    print(f"Running with Config:")
    config.print_config()

    # Determine run mode
    if args.retry_error:
        print("===RETRY failed IDs from error log===")
        product_ids = utils.load_failed_ids(config.ERROR_FILE)
        if not product_ids:
            print("No error record found")
            return
        try:
            asyncio.run(crawler.fetch_all_products(product_ids, retry_mode=True))
        except Exception as e:
            print(f"Error in Retry mode: {e}")
    else:
        print("===Run in NORMAL mode===")
        product_ids = utils.load_product_ids_from_csv(config.INPUT_FILE)

        # Run crawler
        try:
            asyncio.run(crawler.fetch_all_products(product_ids))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
