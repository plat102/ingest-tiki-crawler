import csv
import json
import os
from datetime import datetime
from pathlib import Path


def load_product_ids_from_csv(file_path):
    product_ids = []
    try:
        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Skip header
            header = next(csv_reader)

            for row in csv_reader:
                if row:
                    product_ids.append(int(row[0]))

        print(f"Loaded {len(product_ids)} products")
        return product_ids
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4,  ensure_ascii=False)

def load_json(file_path):
    with open(file_path, encoding='utf-8') as json_file:
        return json.load(json_file)

def clean_description(html):
    pass

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

