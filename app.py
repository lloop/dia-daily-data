"""Flask server for exploring scraped DIA product and price data."""

import json
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template

from config import DATABASE_FILE


def create_app(database_path=None):
    """Create the Flask application, optionally using a test database."""
    app = Flask(__name__)
    app.config['DATABASE_FILE'] = Path(database_path or DATABASE_FILE)

    def query_database(query, parameters=()):
        database_file = app.config['DATABASE_FILE']
        if not database_file.exists():
            return []

        with sqlite3.connect(database_file) as connection:
            connection.row_factory = sqlite3.Row
            return [dict(row) for row in connection.execute(query, parameters)]

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/api/products')
    def products():
        rows = query_database(
            """
            SELECT
                products.id,
                products.name,
                products.item_type,
                products.metadata_json,
                latest.price,
                latest.currency,
                latest.raw_price_per_unit,
                latest.unit_price_eur,
                latest.availability,
                latest.scraped_at
            FROM products
            LEFT JOIN price_logs AS latest
                ON latest.id = (
                    SELECT price_logs.id
                    FROM price_logs
                    WHERE price_logs.product_id = products.id
                    ORDER BY price_logs.scraped_at DESC, price_logs.id DESC
                    LIMIT 1
                )
            ORDER BY products.name
            """
        )

        for row in rows:
            row['metadata'] = json.loads(row.pop('metadata_json') or '{}')

        return jsonify(rows)

    @app.get('/api/products/<int:product_id>/price-history')
    def price_history(product_id):
        rows = query_database(
            """
            SELECT price, currency, raw_price_per_unit, unit_price_eur,
                   availability, scraped_at
            FROM price_logs
            WHERE product_id = ?
            ORDER BY scraped_at, id
            """,
            (product_id,),
        )
        return jsonify(rows)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)