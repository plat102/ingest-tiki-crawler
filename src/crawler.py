"""Main crawl logic"""
import time
import asyncio
import requests
import aiohttp
from config import API_URL, HEADERS, INPUT_FILE
from utils import load_product_ids_from_csv

async def fetch_product(session: aiohttp.ClientSession, product_id: int):
    url = f"{API_URL}/{product_id}"

    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                return {
                    'id': product_id,
                    'name': data['name'],
                    'url_key': data['url_key'],
                    'price': data['price'],
                    'description': data['description'],
                    'short_description': data['short_description'],
                    'images': data['images']
                }
    except Exception as e:
        print(e)
        return None

async def fetch_products(product_ids: list):
    async with aiohttp.ClientSession() as session:
        # Create tasks for all products
        tasks = [fetch_product(session, pid) for pid in product_ids]

        # Run concurrently
        results = await asyncio.gather(*tasks)

        return results

async def main():
    start = time.time()

    ids = load_product_ids_from_csv(INPUT_FILE)

    # Run event loop
    products = await fetch_products(ids)

    end = time.time()
    total_runtime = end - start
    print(f"Got {len(products)} products in {total_runtime} seconds.\
        Est for 200000: {(total_runtime / len(products) * 200000)/(60*60)} hours")

if __name__ == "__main__":
    asyncio.run(main())
