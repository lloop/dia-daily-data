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
    Extract JSON data from HTML content and filter for ListItem entries.
    Looks for JSON-LD ItemList and extracts only items with @type: ListItem.
    
    Args:
        html_content: The HTML content as string
        
    Returns:
        List of filtered ListItem product dictionaries
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    filtered_items = []
    
    # Look for JSON-LD script tags (type="application/ld+json")
    scripts = soup.find_all('script', {'type': 'application/ld+json'})
    
    for script in scripts:
        try:
            data = json.loads(script.string)
            
            # Check if this is an ItemList with itemListElement
            if isinstance(data, dict) and data.get('@type') == 'ItemList':
                item_list_elements = data.get('itemListElement', [])
                
                # Filter for ListItem entries only
                for element in item_list_elements:
                    if isinstance(element, dict) and element.get('@type') == 'ListItem':
                        # Extract the item data from the ListItem
                        item_data = element.get('item', {})
                        # Add position and url for reference
                        list_item = {
                            'position': element.get('position'),
                            'url': element.get('url'),
                            'product': item_data
                        }
                        filtered_items.append(list_item)
        except json.JSONDecodeError:
            continue
    
    return filtered_items


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
    Display a sample of scraped ListItem products.
    
    Args:
        products: List of ListItem dictionaries with product data
        limit: Number of products to display
    """
    if limit is None:
        limit = SAMPLE_SIZE
    
    print(f"\n{'='*60}")
    print(f"Sample of {min(limit, len(products))} items from {len(products)} total:")
    print(f"{'='*60}\n")
    
    for i, list_item in enumerate(products[:limit], 1):
        position = list_item.get('position', 'N/A')
        url = list_item.get('url', 'N/A')
        product = list_item.get('product', {})
        
        # Extract product information
        name = product.get('name', 'N/A')
        image = product.get('image', 'N/A')
        
        offers = product.get('offers', {})
        price = offers.get('price', 'N/A')
        currency = offers.get('priceCurrency', 'EUR')
        availability = offers.get('availability', 'N/A')
        
        print(f"{i}. Position: {position}")
        print(f"   Name: {name}")
        print(f"   Price: {price} {currency}")
        print(f"   Availability: {availability}")
        print(f"   Image: {image}")
        print(f"   URL: {url}\n")


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
