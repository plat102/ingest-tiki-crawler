import csv

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
    pass

def load_json(file_path):
    pass

def clean_description(html):
    pass
