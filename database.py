"""SQLite persistence for daily DIA product and price data."""

import json
import re
import sqlite3
from datetime import datetime, timezone


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    item_type TEXT,
    metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS price_logs (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    price REAL,
    currency TEXT,
    raw_price_per_unit TEXT,
    unit_price_eur REAL,
    availability TEXT,
    scraped_at DATETIME NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""


def initialize_database(database_path):
    """Create the database tables if they do not already exist."""
    with sqlite3.connect(database_path) as connection:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.executescript(SCHEMA)


def parse_unit_price(raw_price_per_unit):
    """Convert a displayed European unit price into a float in euros."""
    if not raw_price_per_unit:
        return None

    match = re.search(r'(\d+[.,]\d+)', raw_price_per_unit)
    if not match:
        return None

    return float(match.group(1).replace(',', '.'))


def save_products_to_database(products, database_path):
    """Upsert products and append one price log for each scraped product."""
    initialize_database(database_path)
    scraped_at = datetime.now(timezone.utc).isoformat(timespec='seconds')

    with sqlite3.connect(database_path) as connection:
        connection.execute('PRAGMA foreign_keys = ON')

        for product in products:
            name = product.get('name')
            if not name:
                continue

            offers = product.get('offers') or {}
            metadata = {
                'type': product.get('type'),
                'info_labels': product.get('info_labels', []),
            }

            connection.execute(
                """
                INSERT INTO products (name, item_type, metadata_json)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    item_type = excluded.item_type,
                    metadata_json = excluded.metadata_json
                """,
                (
                    name,
                    product.get('type'),
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )

            product_id = connection.execute(
                'SELECT id FROM products WHERE name = ?', (name,)
            ).fetchone()[0]

            connection.execute(
                """
                INSERT INTO price_logs (
                    product_id, price, currency, raw_price_per_unit,
                    unit_price_eur, availability, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    offers.get('price'),
                    offers.get('priceCurrency'),
                    product.get('price_per_unit'),
                    parse_unit_price(product.get('price_per_unit')),
                    offers.get('availability'),
                    scraped_at,
                ),
            )

    print(f"Successfully saved {len(products)} products to {database_path}")