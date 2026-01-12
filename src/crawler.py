"""Main crawl logic"""
import time
import asyncio
import random
import aiohttp
from config import *
from utils import save_json, load_checkpoint, save_checkpoint, append_error_log, parse_product_data

async def fetch_product(session: aiohttp.ClientSession,
                        semaphore: asyncio.Semaphore,
                        product_id: int):
    """Fetch single product with semaphore control"""

    url = f"{API_URL}/{product_id}"

    # random sleep
    await asyncio.sleep(random.uniform(REQUEST_RANDOM_SLEEP_MIN, REQUEST_RANDOM_SLEEP_MAX))

    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url) as response:
                    status = response.status

                    if response.status == 200:

                        if attempt > 0:
                            print(f"\t✅ Retry SUCCESS for ID {product_id} after {attempt} attempts")

                        data = await response.json()
                        return {
                            'ok': True,
                            'data': parse_product_data(data)
                        }
                    elif status == 429 or status >= 500:
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                            print(f"\t⚠️ Hit {status} for ID {product_id}. Retrying in {wait_time:.2f}s... (Attempt {attempt + 1}/{MAX_RETRIES})")
                            await asyncio.sleep(wait_time)
                            continue  # Retry
                    else:
                        text = await response.text()
                        return {
                            "ok": False,
                            "product_id": product_id,
                            "error_type": "HTTPError",
                            "status": status,
                            "response": text[:500]
                        }
            except Exception as e:
                # retry request
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                else:
                    return {
                        "ok": False,
                        "product_id": product_id,
                        "error_type": type(e).__name__,
                        "message": str(e)
                    }
    return {
        "ok": False,
        "product_id": product_id,
        "error_type": "UnknownError",
        "message": "Unexpected code path"
    }

async def process_batch(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    batch_ids: list,
    batch_index: int,
    file_prefix: str = 'batch'
):
    """Process batch with semaphore
        - Launch all tasks at once
        - Semaphore control concurrency
    """
    print(f"Batch idx {batch_index}: Processing {len(batch_ids)} products.")

    batch_start_time = time.time()

    # Lauch tasks
    tasks = [
        fetch_product(session, semaphore, pid)
        for pid in batch_ids
    ]

    # Semaphore control numbers of tasks run
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter results
    products = []
    errors  = []

    for pid, result in zip(batch_ids, results):
        if not result:
            errors.append({
                "batch": batch_index,
                "product_id": pid,
                "error_type": "Unknown",
                "message": "Empty result"
            })
            continue

        if isinstance(result, dict) and result.get("ok"):
            products.append(result["data"])
        else:
            errors.append(result)

    success_cnt = len(products)
    error_cnt = len(errors)
    # Save product files
    if products:
        output_file = f'{OUTPUT_DIR}/{file_prefix}_{batch_index:04d}.json'
        save_json(products, output_file)
        print(f'\tSaved {success_cnt} products to {output_file}')

    # Save & log error
    for error in errors:
        append_error_log(ERROR_FILE,{
            'batch': batch_index,
            **error
        })
    if error_cnt > 0:
        print(f'\tSaved {error_cnt} (after retries) errors to {ERROR_FILE}')

    batch_time = time.time() - batch_start_time
    print(f'\tTime: {batch_time:.2f}s')

    return len(products), error_cnt

async def fetch_all_products(product_ids: list, retry_mode: bool=False):

    if retry_mode:
        print(f"\nRun mode: RETRY (ignore checkpoint)")
        start_batch = 0
        file_prefix = 'retry_batch'
    else:
        # Load checkpoint
        last_batch = load_checkpoint(CHECKPOINT_FILE)
        start_batch = last_batch + 1
        file_prefix = 'batch'
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
                session, semaphore, batch_ids, batch_idx, file_prefix
            )
            total_products += success
            total_errors += error

            # Save checkpoint
            if not retry_mode:
                save_checkpoint(batch_idx, CHECKPOINT_FILE)

            # Small delay between batches
            await asyncio.sleep(DELAY_AFTER_BATCH)

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
