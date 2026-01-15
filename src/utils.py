import csv
import json
import os
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from schema import Product

def load_product_ids_from_csv(file_path):
    product_ids = set()
    try:
        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Skip header
            header = next(csv_reader)

            for row in csv_reader:
                if row:
                    product_ids.add(int(row[0]))

        print(f"Loaded {len(product_ids)} products id from {file_path}")
        return list(product_ids)
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None

def save_json(data, file_path):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4,  ensure_ascii=False)

def load_json(file_path):
    with open(file_path, encoding='utf-8') as json_file:
        return json.load(json_file)

def clean_description(html):
    # parse HTML
    soup = BeautifulSoup(html, "html.parser") #TODO: any faster parser?

    # Get text
    txt = soup.get_text(separator='\n')
    lines = [line.strip()
             for line in txt.splitlines()
             if line.strip()]
    cleaned_lines = '\n'.join(lines)

    return cleaned_lines

def parse_product_data_manual(raw_data):
    if not raw_data:
        return None

    raw_images = raw_data.get("images", [])
    image_urls = []
    if raw_images:
        image_urls = [
            img.get('base_url')
            for img in raw_images
            if img.get('base_url')
        ]

    return {
        "id": raw_data.get("id"),
        "name": raw_data.get("name"),
        "url_key": raw_data.get("url_key"),
        "price": raw_data.get("price"),
        "description": clean_description(raw_data.get("description", "")),
        "image_urls": image_urls
    }


def parse_product_data(raw_data: dict):
    if not raw_data:
        return None
    # Validate & transform
    try:
        product = Product(
            id=raw_data.get("id",0),
            name=raw_data.get("name", "name not found"),
            url_key=raw_data.get("url_key"),
            price=raw_data.get("price", 0),
            description=raw_data.get("description"),
            image_urls=raw_data.get("images", [])
        )

        return product.model_dump()
    except Exception as e:
        print(e)

def append_error_log(file_path, record: dict):
    """
    Append error record (JSON Lines)
    """

    record["timestamp"] = datetime.utcnow().isoformat()

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_checkpoint(checkpoint_file):
    if not os.path.isfile(checkpoint_file):
        return -1
    try:
        checkpoint = load_json(checkpoint_file)
        if checkpoint and 'last_batch' in checkpoint:
            return checkpoint['last_batch']
        return -1
    except json.JSONDecodeError:
        return -1

def save_checkpoint(batch_index, file_path):
    checkpoint = {
        'last_batch': batch_index,
        'timestamp': datetime.now().isoformat()
    }
    save_json(checkpoint, file_path)

def load_failed_ids(file_path):
    path = Path(file_path)
    if not os.path.isfile(file_path):
        print(f'No error file found at {file_path}')
        return

    failed_ids = set()
    try:
        with open(file_path, encoding='utf-8') as csv_file:
            for line in csv_file:
                try:
                    error_record = json.loads(line.strip())
                    pid = error_record.get("product_id")
                    if pid:
                        failed_ids.add(int(pid))
                except json.JSONDecodeError:
                    continue
        failed_list = sorted(list(failed_ids))
        print(f"Loaded {len(failed_list)} failed ids from {file_path}")

        if path.exists():
            backup_error_log(path)

        return failed_list
    except Exception as e:
        print(f"Failed to load failed ids from {file_path}")

def backup_error_log(file_path: Path | str):
    path = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(f"{path.name}.{timestamp}.bak")

    try:
        file_path.rename(backup_path)
        print(f"Log backed up to: {backup_path.name}")
    except Exception as e:
        print(f"Could not backup file: {e}")
