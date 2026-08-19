# Quotes Scraper

A Python web scraper that extracts all quotes from [quotes.toscrape.com](http://quotes.toscrape.com/), a website designed for testing web scraping projects.

## Features

- ✅ Scrapes all quotes across multiple pages
- ✅ Extracts quote text, author, and associated tags
- ✅ Handles pagination automatically
- ✅ Configurable settings via `config.py`
- ✅ Saves output to JSON format
- ✅ Includes unit tests
- ✅ Error handling for network issues
- ✅ Organized logging

## Project Structure

```
quotes_scraper/
├── scrape-quotes-excercise.py    # Main scraper script
├── test-scrape-quotes.py          # Unit tests
├── config.py                       # Configuration (local, not committed)
├── config.example.py               # Configuration template
├── output/                         # Generated output files (not committed)
├── logs/                           # Log files (not committed)
└── README.md                       # This file
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies:**
   ```bash
   pip install requests beautifulsoup4
   ```

3. **Create configuration file:**
   ```bash
   cp config.example.py config.py
   ```

4. **Customize settings** (optional):
   Edit `config.py` to adjust timeouts, output format, page limits, etc.

## Usage

### Run the scraper

```bash
python scrape-quotes-excercise.py
```

**Output:**
- Displays progress as it scrapes each page
- Shows a sample of the scraped quotes
- Saves all quotes to `output/quotes.json`

### Run tests

```bash
python -m unittest test-scrape-quotes.py
```

## Configuration

All settings are defined in `config.py`. Key settings include:

| Setting | Purpose | Default |
|---------|---------|---------|
| `BASE_URL` | Target website URL | `http://quotes.toscrape.com` |
| `TIMEOUT` | Request timeout in seconds | `10` |
| `MAX_PAGES` | Maximum pages to scrape | `None` (all pages) |
| `OUTPUT_FILE` | Where to save quotes | `output/quotes.json` |
| `DISPLAY_SAMPLE` | Show sample quotes after scraping | `True` |
| `SAMPLE_SIZE` | Number of sample quotes to display | `5` |

### Using `config.example.py`

The `config.example.py` file is committed to the repository and shows what configuration options are available. Never commit your personal `config.py` file—it's in `.gitignore` for a reason.

To reset to defaults:
```bash
cp config.example.py config.py
```

## Output Format

The scraper saves quotes to JSON in this format:

```json
[
  {
    "text": "\"The way to get started is to quit talking and begin doing.\"",
    "author": "Walt Disney",
    "tags": ["action", "inspire", "motivation"]
  },
  ...
]
```

## Troubleshooting

### Connection timeout
Increase `TIMEOUT` in `config.py` if the website is slow.

### ModuleNotFoundError
Install missing dependencies:
```bash
pip install requests beautifulsoup4
```

### Tests failing
Make sure you have the latest dependencies and Python 3.7+:
```bash
python --version
```

## Notes

- This scraper is designed for the practice website `quotes.toscrape.com`
- Always respect robots.txt and website terms of service when scraping
- The scraper includes polite delays between requests via User-Agent headers

## License

This project is for educational purposes.
