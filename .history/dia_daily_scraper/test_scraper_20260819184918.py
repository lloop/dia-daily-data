"""
Unit tests for the DIA Daily Scraper
"""

import unittest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from scraper import (
    extract_json_from_html,
    extract_product_page_data,
    has_tomato_product_type,
    scrape_tomatoes,
)
from database import parse_unit_price, save_products_to_database


class TestJSONExtraction(unittest.TestCase):
    """Test cases for JSON extraction from HTML."""

    def test_extract_list_items_from_json_ld(self):
        """Test extracting ListItem entries from the category page."""
        html = '''
        <html>
            <script type="application/ld+json">
                {"@type": "ItemList", "itemListElement": [
                    {"@type": "ListItem", "position": 1,
                     "url": "https://www.dia.es/product/1",
                     "item": {"@type": "Product", "name": "Tomate"}},
                    {"@type": "Product", "name": "Not a list item"}
                ]}
            </script>
        </html>
        '''
        products = extract_json_from_html(html)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product']['name'], 'Tomate')

    def test_empty_html(self):
        """Test with empty HTML."""
        self.assertEqual(extract_json_from_html('<html></html>'), [])


class TestProductPageFiltering(unittest.TestCase):
    """Test filtering based on product-page metadata."""

    def test_accepts_tomato_product_type(self):
        html = '''
        <ul class="info-label__list"><li>Tipo de producto: Tomates</li></ul>
        '''
        self.assertTrue(has_tomato_product_type(html))

    def test_rejects_other_product_type(self):
        html = '''
        <ul class="info-label__list"><li>Tipo de producto: Pimientos</li></ul>
        '''
        self.assertFalse(has_tomato_product_type(html))

    def test_extracts_selected_product_page_data(self):
        html = '''
        <p class="buy-box__price-per-unit">2,58 €/KILO</p>
        <ul class="info-label__list">
            <li>Tipo de producto: Tomates</li>
            <li>Formato: Bandeja</li>
        </ul>
        '''
        product = {
            '@type': 'Product',
            'image': 'not included',
            'name': 'Tomate pera',
            'offers': {'@type': 'Offer', 'price': 1.29, 'priceCurrency': 'EUR'},
        }

        result = extract_product_page_data(html, product)

        self.assertEqual(result, {
            'type': 'Product',
            'name': 'Tomate pera',
            'offers': {'@type': 'Offer', 'price': 1.29, 'priceCurrency': 'EUR'},
            'price_per_unit': '2,58 €/KILO',
            'info_labels': ['Tipo de producto: Tomates', 'Formato: Bandeja'],
        })


class TestScraper(unittest.TestCase):
    """Test cases for the scraper functions."""

    @patch('scraper.fetch_page')
    def test_scrape_tomatoes_keeps_only_matching_product_pages(self, mock_fetch):
        category_response = Mock(status_code=200, text='''
            <script type="application/ld+json">
            {"@type":"ItemList","itemListElement":[
                            {"@type":"ListItem","position":1,"url":"https://dia.test/tomato",
                             "item":{"@type":"Product","name":"Tomate","offers":{"price":1.29}}},
              {"@type":"ListItem","position":2,"url":"https://dia.test/pepper","item":{}}
            ]}
            </script>
        ''')
        tomato_response = Mock(text='''
            <p class="buy-box__price-per-unit">1,29 €/KILO</p>
            <ul class="info-label__list"><li>Tipo de producto: Tomates</li></ul>
        ''')
        pepper_response = Mock(text='<ul class="info-label__list"><li>Tipo de producto: Pimientos</li></ul>')
        mock_fetch.side_effect = [category_response, tomato_response, pepper_response]

        products = scrape_tomatoes()

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], 'Tomate')
        self.assertEqual(products[0]['price_per_unit'], '1,29 €/KILO')


class TestDatabase(unittest.TestCase):
    """Test product upserts and daily price logging."""

    def test_saves_new_product_and_price_log(self):
        product = {
            'type': 'Product',
            'name': 'Tomate pera',
            'offers': {
                'price': 1.29,
                'priceCurrency': 'EUR',
                'availability': 'https://schema.org/InStock',
            },
            'price_per_unit': '(2,58 €/KILO)',
            'info_labels': ['Tipo de producto: Tomates'],
        }

        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / 'products.sqlite3'
            save_products_to_database([product], database_path)

            with sqlite3.connect(database_path) as connection:
                product_row = connection.execute(
                    'SELECT name, item_type, metadata_json FROM products'
                ).fetchone()
                log_row = connection.execute(
                    """SELECT price, currency, raw_price_per_unit,
                    unit_price_eur, availability FROM price_logs"""
                ).fetchone()

            self.assertEqual(product_row[0:2], ('Tomate pera', 'Product'))
            self.assertIn('Tipo de producto: Tomates', product_row[2])
            self.assertEqual(log_row, (
                1.29,
                'EUR',
                '(2,58 €/KILO)',
                2.58,
                'https://schema.org/InStock',
            ))

    def test_existing_product_gets_an_additional_price_log(self):
        product = {
            'type': 'Product',
            'name': 'Tomate pera',
            'offers': {'price': 1.29, 'priceCurrency': 'EUR'},
            'price_per_unit': '(2,58 €/KILO)',
            'info_labels': [],
        }

        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / 'products.sqlite3'
            save_products_to_database([product], database_path)
            save_products_to_database([product], database_path)

            with sqlite3.connect(database_path) as connection:
                product_count = connection.execute(
                    'SELECT COUNT(*) FROM products'
                ).fetchone()[0]
                log_count = connection.execute(
                    'SELECT COUNT(*) FROM price_logs'
                ).fetchone()[0]

            self.assertEqual(product_count, 1)
            self.assertEqual(log_count, 2)

    def test_parse_unit_price(self):
        self.assertEqual(parse_unit_price('(2,58 €/KILO)'), 2.58)
        self.assertIsNone(parse_unit_price(None))


if __name__ == "__main__":
    unittest.main()
