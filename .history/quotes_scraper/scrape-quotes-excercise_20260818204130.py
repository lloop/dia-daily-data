import requests
from bs4 import BeautifulSoup
import json
from config import (
    BASE_URL, HEADERS, TIMEOUT, OUTPUT_FILE, PAGINATION_ENABLED, MAX_PAGES,
    QUOTE_CONTAINER_CLASS, QUOTE_TEXT_CLASS, AUTHOR_CLASS, TAG_CLASS,
    DISPLAY_SAMPLE, SAMPLE_SIZE, ensure_directories
)

def scrape_quotes():
    """
    Scrapes all quotes from http://quotes.toscrape.com/
    Handles pagination across multiple pages.
    """
    all_quotes = []
    page_num = 1
    
    while True:
        # Check page limit from config
        if MAX_PAGES and page_num > MAX_PAGES:
            print(f"Reached maximum page limit ({MAX_PAGES}). Stopping.")
            break
        
        # Construct the URL for the current page
        if page_num == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}/page/{page_num}/"
        
        print(f"Scraping page {page_num}: {url}")
        
        try:
            # Fetch the page with timeout and headers from config
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()  # Raise an error for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            break
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all quote containers using configured class name
        quote_containers = soup.find_all('div', class_=QUOTE_CONTAINER_CLASS)
        
        # If no quotes found, we've reached the end
        if not quote_containers:
            print(f"No more quotes found. Stopping at page {page_num}.")
            break
        
        # Extract quote data
        for container in quote_containers:
            # Get quote text
            quote_text = container.find('span', class_='text').get_text(strip=True)
            
            # Get author name
            author = container.find('small', class_='author').get_text(strip=True)
            
            # Get tags
            tag_elements = container.find_all('a', class_='tag')
            tags = [tag.get_text(strip=True) for tag in tag_elements]
            
            # Create quote dictionary
            quote_dict = {
                'text': quote_text,
                'author': author,
                'tags': tags
            }
            
            all_quotes.append(quote_dict)
        
        print(f"  Found {len(quote_containers)} quotes on this page")
        
        # Check if there's a next page button
        next_btn = soup.find('li', class_='next')
        if not next_btn:
            print("No next page button found. Finished scraping.")
            break
        
        page_num += 1
    
    return all_quotes


def save_quotes_to_json(quotes, filename='quotes.json'):
    """Save the scraped quotes to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(quotes, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully saved {len(quotes)} quotes to {filename}")


def display_quotes(quotes, limit=5):
    """Display a sample of the scraped quotes."""
    print(f"\n{'='*60}")
    print(f"Sample of {min(limit, len(quotes))} quotes from {len(quotes)} total:")
    print(f"{'='*60}\n")
    
    for i, quote in enumerate(quotes[:limit], 1):
        print(f"{i}. {quote['text']}")
        print(f"   - {quote['author']}")
        print(f"   Tags: {', '.join(quote['tags'])}\n")


if __name__ == "__main__":
    print("Starting web scraper for quotes.toscrape.com...\n")
    
    # Scrape all quotes
    quotes = scrape_quotes()
    
    # Display results
    print(f"\n✓ Successfully scraped {len(quotes)} total quotes!")
    display_quotes(quotes, limit=5)
    
    # Save to JSON file
    save_quotes_to_json(quotes)
