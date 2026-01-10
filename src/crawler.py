"""Main crawl logic"""
import requests
from config import API_URL, HEADERS, INPUT_FILE
from utils import load_product_ids_from_csv

def fetch_product(product_id: int):
    response = requests.get(f"{API_URL}/product-detail/api/v1/products/{product_id}", headers=HEADERS)

    if response.status_code == 200:
        data = response.json()

        return {
            'id': product_id,
            'name': data['name'],
            'url_key': data['url_key'],
            'price': data['price'],
            'description': data['description'],
            'short_description': data['short_description'],
            'images': data['images']
        }
    else:
        return None

def main():
    ids = load_product_ids_from_csv(INPUT_FILE)
    products = []

    for pid in ids:
        product = fetch_product(pid)
        if product:
            products.append(product)

    print(f"Got {len(products)} products")
    print(products)

if __name__ == "__main__":
    main()
