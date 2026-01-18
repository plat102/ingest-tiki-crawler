# Tiki Product Crawler

An asynchronous Python crawler designed to ingest product data from Tiki.vn.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Poetry](https://img.shields.io/badge/dependency-poetry-purple)

## Key Features
* **Asynchronous arrchitecture:** Built with `aiohttp` and `asyncio` to handle high concurrency and maximize throughput.
* **Fault tolerance:** Implements automatic checkpointing. If the process is interrupted, it resumes from the last successful batch.
* **Error log retry mechanism:**
    * Logs failed requests (404, 500, Timeout) .
    * `--retry-error` mode to re-process only failed IDs with automatic log rotation.
* **Data validation:** Strict schema validation using **Pydantic** to ensure data quality.
* **Configurable:** Fully customizable via environment variables (concurrency, timeouts, batch sizes).

### Example output data
Run completed log:
```txt
============================================================
✅ COMPLETED!
============================================================
Products saved: 198942
Errors: 1058
Time: 63.07 minutes
Speed: 52.86 products/second
============================================================
```
![img.png](docs/images/output_ls.png)

> **Sample products file:** https://gist.github.com/plat102/cc9a3d2f31401a69fd4ff5f30f301bb6

## Set up & Usage

This crawler can be run either using Docker or Locally.

**Clone & Config:**
```bash
git clone https://github.com/plat102/ingest-tiki-crawler
cd ingest-tiki-crawler
cp .env.example .env
```

### Option 1: Docker

**Prerequisites:** Docker & Docker Compose installed.
1. **Start Crawler (Background Mode):**
    This command builds the image and starts the worker with auto-restart policy enabled.
    ```bash
    docker compose up -d
    ```

2. **Monitor Logs:**
    ```bash
    docker compose logs -f
    ```

3. **Run Retry Mode (Ad-hoc):**
    To run the crawler in `--retry-error` mode inside a temporary container:
    ```bash
    # Stop the main worker first to avoid file conflicts
    docker compose stop

    # Run retry command
    docker compose run --rm tiki-crawler python src/main.py --retry-error
    ```

### Option 2: Run Locally (Development)

**Prerequisites:** Python >= 3.12, Poetry.

1.  **Install dependencies:**
    ```bash
    poetry install
    ```

2. **Run Normal Crawl:**
    ```bash
    poetry run python src/main.py
    ```

3. **Run Retry Errors:**
    ```bash
    poetry run python src/main.py --retry-error
    ```

### Configuration (`.env`)

#### Note on Rate Limiting
If you encounter `HTTP 429 Too Many Requests` too often, pls try:
- reduce `MAX_CONCURRENT_TASKS`
- increase `DELAY_AFTER_BATCH`
- increase `REQUEST_RANDOM_SLEEP_MIN`
- increase `REQUEST_RANDOM_SLEEP_MAX`

## Load into Database
This project also allows loading crawled JSON into PostgreSQL for persistent storage.

* **High Performance:** Uses `psycopg2` for bulk inserts.
* **Idempotent:** Implements `ON CONFLICT DO UPDATE` to prevent duplicates.
* **Flexible:** Stores raw data using `JSONB`.

Usage:
1. **Set up Database:**

    Set credentials in `.env` file
2. **Initialize schema (run once):**
    ```bash
    poetry run python -m src.scripts.init_db
    ```
3. Load data
    ```bash
    poetry run python -m src.scripts.run_load_db
    ```
Example logs:
```shell
(ingest-tiki-crawler-py3.12) ➜  tiki-crawl git:(dev) ✗ python -m src.scripts.run_load_db
===== Starting database loading...
DEBUG: Searching in path: /home/thu/repo/project/tiki-crawl/data/products/batch_*.json
Found 200 JSON files.
 [PostgreSQL client] Loaded batch of 999 products
 [PostgreSQL client] Loaded batch of 998 products
 [PostgreSQL client] Loaded batch of 999 products
```

## Contributing
Pull requests are welcome.<br>
For major changes, please open an issue to discuss what you would like to change. Thanks.