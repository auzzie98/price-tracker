"""Build sku_prices, then index_values, from observations.

Run: python scripts\build_derived.py
Must be safe to rerun. Must not duplicate rows.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_tracker.config import load_settings, repo_root
from price_tracker.db import connect, init_database
from price_tracker.index import build_sku_prices, build_index_values


def main() -> None:
    root = repo_root()
    settings = load_settings()
    database_path = settings.get("database_path", "data/price-tracker.db")
    if not Path(database_path).is_absolute():
        database_path = root / database_path

    schema_path = root / "db" / "schema.sql"
    init_database(database_path, schema_path)

    conn = connect(database_path)
    try:
        build_sku_prices(conn)
        build_index_values(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
