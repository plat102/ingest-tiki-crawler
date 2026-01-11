"""Main crawl logic"""
import time
import asyncio
from datetime import timedelta
import aiohttp
from config import *
from utils import load_product_ids_from_csv, save_json, load_checkpoint, save_checkpoint

async def fetch_product(session: aiohttp.ClientSession,
                        semaphore: asyncio.Semaphore,
                        product_id: int):
    """Fetch single product with semaphore control"""

    url = f"{API_URL}/{product_id}"

    async with semaphore:
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

async def process_batch(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    batch_ids: list,
    batch_index: int
):
    """Process batch with semaphore
        - Launch all tasks at once
        - Semaphore control concurrency
    """
    print(f"Batch {batch_index+1}: Processing {len(batch_ids)} products.")

    batch_start_time = time.time()

    # Lauch tasks
    tasks = [
        fetch_product(session, semaphore, pid)
        for pid in batch_ids
    ]

    # Semaphore control numbers of tasks run
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter success/error
    products = []
    errors_cnt = 0

    for result in results:
        if isinstance(result, Exception):
            errors_cnt += 1
        elif result is not None:
            products.append(result)
        else:
            errors_cnt += 1

    if products:
        output_file = f'{OUTPUT_DIR}/batch_{batch_index:04d}.json'
        save_json(products, output_file)
        print(f'\tSaved {len(products)} products to {output_file}')

    if errors_cnt > 0:
        print(f'\tErrors {errors_cnt} out of {len(batch_ids)} products.')

    batch_time = time.time() - batch_start_time
    print(f'\tTime: {batch_time:.2f}s')

    return len(products), errors_cnt

async def fetch_all_products(product_ids: list):

    # Load checkpoint
    last_batch = load_checkpoint(CHECKPOINT_FILE)
    start_batch = last_batch + 1
    total_batches = (len(product_ids) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\n{'='*60}")
    print(f"CRAWL STATUS")
    print(f"{'='*60}")
    print(f"Total products: {len(product_ids):,}")
    print(f"Total batches: {total_batches}. Starting from batch: {start_batch}\n")

    if start_batch >= total_batches:
        print("\nAll batches completed!")
        return

    # Process batches
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_TASKS)

    total_products = 0
    total_errors = 0
    total_start = time.time()

    async with aiohttp.ClientSession(
        headers=HEADERS,
        connector=connector,
        timeout=timeout
    ) as session:
        # Process each batch
        for batch_idx in range(start_batch, total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx+BATCH_SIZE, len(product_ids))
            batch_ids = product_ids[start_idx:end_idx]

            success, error = await process_batch(
                session,
                semaphore,
                batch_ids,
                batch_idx
            )
            total_products += success
            total_errors += error

            # Save checkpoint
            save_checkpoint(batch_idx, CHECKPOINT_FILE)

            # Small delay between batches
            await asyncio.sleep(0.5)

    # Summary
    total_time = time.time() - total_start

    print(f"\n{'=' * 60}")
    print(f"✅ COMPLETED!")
    print(f"{'=' * 60}")
    print(f"Products saved: {total_products}")
    print(f"Errors: {total_errors}")
    print(f"Time: {total_time / 60:.2f} minutes")
    print(f"Speed: {len(product_ids) / total_time:.2f} products/second")
    print(f"{'=' * 60}")

async def main():

    product_ids = load_product_ids_from_csv(INPUT_FILE)

    # Estimate
    est_seconds = (len(product_ids) / MAX_CONCURRENT_TASKS) * 0.5 * 1.2
    print("Estimated time:", str(timedelta(seconds=int(est_seconds))))

    # Crawl
    await fetch_all_products(product_ids)

if __name__ == "__main__":
    asyncio.run(main())
