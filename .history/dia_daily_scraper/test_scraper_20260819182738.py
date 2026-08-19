"""
Unit tests for the DIA Daily Scraper
"""

import unittest
from unittest.mock import Mock, patch
from scraper import (
    extract_json_from_html,
    extract_product_page_data,
    has_tomato_product_type,
    scrape_tomatoes,
)


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


if __name__ == "__main__":
    unittest.main()
