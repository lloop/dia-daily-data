import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app
from database import initialize_database


class TestApp(unittest.TestCase):
    def test_api_returns_products_and_history(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / 'products.sqlite3'
            initialize_database(database_path)
            with sqlite3.connect(database_path) as connection:
                connection.execute(
                    "INSERT INTO products (name, item_type, metadata_json) VALUES (?, ?, ?)",
                    ('Tomate pera', 'Product', json.dumps({'info_labels': []})),
                )
                product_id = connection.execute('SELECT id FROM products').fetchone()[0]
                connection.execute(
                    """INSERT INTO price_logs
                    (product_id, price, currency, raw_price_per_unit,
                     unit_price_eur, availability, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (product_id, 1.29, 'EUR', '(2,58 €/KILO)', 2.58,
                     'InStock', '2026-08-19T10:00:00+00:00'),
                )

            client = create_app(database_path).test_client()
            products_response = client.get('/api/products')
            history_response = client.get(f'/api/products/{product_id}/price-history')

            self.assertEqual(products_response.status_code, 200)
            self.assertEqual(products_response.json[0]['name'], 'Tomate pera')
            self.assertEqual(products_response.json[0]['unit_price_eur'], 2.58)
            self.assertEqual(history_response.status_code, 200)
            self.assertEqual(history_response.json[0]['price'], 1.29)

    def test_index_page_loads(self):
        client = create_app('/tmp/does-not-exist.sqlite3').test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product price history', response.data)


if __name__ == '__main__':
    unittest.main()