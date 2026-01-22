from schema import Product

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
