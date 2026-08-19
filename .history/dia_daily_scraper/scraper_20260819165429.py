"""
DIA Daily Scraper

Scrapes product data from Día supermarket website (https://www.dia.es)
Fetches JSON data from product pages and extracts item information.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from config import (
    BASE_URL, TOMATOES_URL, HEADERS, TIMEOUT, OUTPUT_FILE,
    DISPLAY_SAMPLE, SAMPLE_SIZE, ensure_directories
)


def fetch_page(url):
    """
    Fetch a page and return the response.
    
    Args:
        url: The full URL to fetch
        
    Returns:
        requests.Response object or None if error
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_json_from_html(html_content):
    """
    Extract JSON data from HTML content.
    Looks for JSON embedded in script tags or as data attributes.
    
    Args:
        html_content: The HTML content as string
        
    Returns:
        List of product dictionaries or empty list if not found
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    # Look for JSON in script tags (common pattern)
    scripts = soup.find_all('script', {'type': 'application/json'})
    
    for script in scripts:
        try:
            data = json.loads(script.string)
            # Try to extract products from various possible structures
            if isinstance(data, dict):
                # Check common JSON response structures
                if 'products' in data:
                    if isinstance(data['products'], list):
                        products.extend(data['products'])
                elif 'items' in data:
                    if isinstance(data['items'], list):
                        products.extend(data['items'])
                elif 'data' in data:
                    if isinstance(data['data'], list):
                        products.extend(data['data'])
            elif isinstance(data, list):
                products.extend(data)
        except json.JSONDecodeError:
            continue
    
    # Also check for JSON in script tags with specific patterns
    all_scripts = soup.find_all('script')
    for script in all_scripts:
        if script.string:
            # Look for JSON-like patterns in regular scripts
            json_matches = re.findall(r'\{[^{}]*"[^"]*"[^{}]*\}', script.string)
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict):
                        products.append(data)
                except json.JSONDecodeError:
                    continue
    
    return products


def scrape_tomatoes():
    """
    Scrape tomato products from Día website.
    
    Returns:
        List of product dictionaries
    """
    full_url = BASE_URL + TOMATOES_URL
    print(f"Fetching: {full_url}")
    
    response = fetch_page(full_url)
    if not response:
        return []
    
    print(f"Status Code: {response.status_code}")
    
    # Extract JSON data from the page
    products = extract_json_from_html(response.text)
    
    print(f"Found {len(products)} items in JSON data")
    
    return products


def save_products(products):
    """
    Save products to JSON file.
    
    Args:
        products: List of product dictionaries
    """
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully saved {len(products)} products to {OUTPUT_FILE}")


def display_products(products, limit=None):
    """
    Display a sample of scraped products.
    
    Args:
        products: List of product dictionaries
        limit: Number of products to display
    """
    if limit is None:
        limit = SAMPLE_SIZE
    
    print(f"\n{'='*60}")
    print(f"Sample of {min(limit, len(products))} products from {len(products)} total:")
    print(f"{'='*60}\n")
    
    for i, product in enumerate(products[:limit], 1):
        print(f"{i}. Product Data:")
        if isinstance(product, dict):
            for key, value in product.items():
                print(f"   {key}: {value}")
        else:
            print(f"   {product}")
        print()


def main():
    """Main function to run the scraper."""
    ensure_directories()
    
    print("DIA Daily Scraper - Starting tomatoes scrape...\n")
    
    # Scrape tomato products
    products = scrape_tomatoes()
    
    if products:
        print(f"\n✓ Successfully scraped {len(products)} products!")
        display_products(products)
        save_products(products)
    else:
        print("\n✗ No products found. Check the URL and page structure.")


if __name__ == "__main__":
    main()
