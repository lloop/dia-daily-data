"""
Unit tests for the DIA Daily Scraper
"""

import unittest
import json
from pathlib import Path
from scraper import extract_json_from_html, scrape_tomatoes


class TestJSONExtraction(unittest.TestCase):
    """Test cases for JSON extraction from HTML."""

    def test_extract_json_from_simple_html(self):
        """Test extracting JSON from script tag."""
        html = '''
        <html>
            <script type="application/json">
                [{"name": "Tomato 1", "price": "2.50"}, {"name": "Tomato 2", "price": "3.00"}]
            </script>
        </html>
        '''
        products = extract_json_from_html(html)
        self.assertGreater(len(products), 0)

    def test_extract_json_with_products_key(self):
        """Test extracting JSON with 'products' key."""
        html = '''
        <html>
            <script type="application/json">
                {"products": [{"name": "Tomato", "price": "2.50"}]}
            </script>
        </html>
        '''
        products = extract_json_from_html(html)
        self.assertGreater(len(products), 0)

    def test_empty_html(self):
        """Test with empty HTML."""
        html = '<html></html>'
        products = extract_json_from_html(html)
        self.assertEqual(len(products), 0)


class TestScraper(unittest.TestCase):
    """Test cases for the scraper functions."""

    def test_scrape_tomatoes_returns_list(self):
        """Test that scrape_tomatoes returns a list."""
        products = scrape_tomatoes()
        self.assertIsInstance(products, list)

    def test_product_structure(self):
        """Test that products have expected structure."""
        products = scrape_tomatoes()
        if products:
            # If we get products, they should be dict-like
            self.assertTrue(
                any(isinstance(p, dict) for p in products),
                "At least one product should be a dictionary"
            )


if __name__ == "__main__":
    unittest.main()
