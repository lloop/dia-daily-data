# DIA Daily Scraper

A Python web scraper for collecting daily data from https://www.dia.es.

## Features

- 🚀 TODO: Add features as development progresses
- ✅ Configurable settings via `config.py`
- ✅ Organized project structure
- ✅ Includes unit tests

## Project Structure

```
dia_daily_scraper/
├── scraper.py                # Main scraper script
├── database.py               # SQLite schema and persistence
├── test_scraper.py           # Unit tests
├── config.py                 # Configuration (local, not committed)
├── config.example.py         # Configuration template
├── output/                   # Generated output files (not committed)
├── logs/                     # Log files (not committed)
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Navigate to the project directory**

2. **Install dependencies:**
   ```bash
   pip install requests beautifulsoup4
   ```

3. **Create configuration file:**
   ```bash
   cp config.example.py config.py
   ```

4. **Customize settings**:
   - Edit `config.py` to add the target URL and adjust other settings
   - Update the `BASE_URL` with the website you want to scrape

## Usage

### Run the scraper

```bash
python scraper.py
```

The scraper stores data in `output/dia_products.sqlite3`. It creates a
`products` table for unique product names and a `price_logs` table with one
price snapshot per scraped product and run. The generated SQLite file is
ignored by Git.

### Run tests

```bash
python -m unittest test_scraper.py
```

## Configuration

All settings are defined in `config.py`. Key settings include:

| Setting | Purpose | Default |
|---------|---------|---------|
| `BASE_URL` | Target website URL | `http://example.com` |
| `TIMEOUT` | Request timeout in seconds | `10` |
| `MAX_PAGES` | Maximum pages to scrape | `None` (all pages) |
| `DATABASE_FILE` | SQLite database path | `output/dia_products.sqlite3` |
| `DISPLAY_SAMPLE` | Show sample data after scraping | `True` |

## Development Status

This project is currently under development. Key tasks:

- [ ] Implement scraper logic
- [ ] Add parsing for target website
- [ ] Write comprehensive tests
- [ ] Add error handling
- [ ] Document output format
- [ ] Add logging

## Notes

- Always respect robots.txt and website terms of service when scraping
- Include polite delays between requests
- Add appropriate User-Agent headers

## License

This project is for educational purposes.
