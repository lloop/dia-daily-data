"""
Configuration template for the DIA Daily scraper project.

To use this project:
1. Copy this file: cp config.example.py config.py
2. Customize the settings in config.py as needed
3. Never commit config.py to the repository

Centralized settings for scraping, output, and logging.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Scraper settings
BASE_URL = "https://www.example.com"  # TODO: Update with actual base URL
OIL_URL = "/path/to/oil/products"  # TODO: Update with actual URL path
EGGS_URL = "/path/to/eggs/products"  # TODO: Update with actual URL path
TOMATOES_URL = "/path/to/tomatoes/products"  # TODO: Update with actual URL path
TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries

# Request settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Output settings
OUTPUT_FORMAT = "json"  # Options: json, csv
OUTPUT_FILE = OUTPUT_DIR / "data.json"
OUTPUT_CSV_FILE = OUTPUT_DIR / "data.csv"
DATABASE_FILE = OUTPUT_DIR / "dia_products.sqlite3"
PRETTY_PRINT = True
ENCODING = "utf-8"

# Logging settings
LOG_FILE = LOGS_DIR / "scraper.log"
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Pagination settings (if applicable)
PAGINATION_ENABLED = True
MAX_PAGES = None  # None for unlimited, set to a number to limit pages

# Display settings
DISPLAY_SAMPLE = True
SAMPLE_SIZE = 5


def ensure_directories():
    """Create necessary directories if they don't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Print configuration on module execution
    ensure_directories()
    print("Configuration loaded successfully!")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Logs directory: {LOGS_DIR}")
    print(f"Base URL: {BASE_URL}")
