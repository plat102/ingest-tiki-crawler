import csv
import pytest
from src.utils import load_product_ids_from_csv


# Create fake csv file
@pytest.fixture
def mock_csv_file(tmp_path):
    d = tmp_path / "input"
    d.mkdir()
    p = d / "test_products.csv"

    # Ghi dữ liệu giả: Có ID trùng lặp (12345 xuất hiện 2 lần)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name"])  # Header
        writer.writerow(["12345", "Product A"])
        writer.writerow(["67890", "Product B"])
        writer.writerow(["12345", "Product A (Duplicate)"])

    return str(p)


def test_load_product_ids_removes_duplicates(mock_csv_file):
    """Test if duplicated IDs are removed"""
    ids = load_product_ids_from_csv(mock_csv_file)

    assert len(ids) == 2 # (12345, 67890)
    assert 12345 in ids
    assert 67890 in ids
    assert isinstance(ids, list)
