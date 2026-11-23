r"""Create the database from db/schema.sql.

Safe to run twice. Must not delete existing observations.
Run: python scripts\init_db.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the src folder importable so the price_tracker package can be used
# when this script is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_tracker.config import load_settings, repo_root
from price_tracker.db import init_database


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize the Price Tracker database from db/schema.sql."
    )
    parser.add_argument(
        "--database",
        help="Path to the SQLite database file (overrides config/settings.yaml).",
    )
    parser.add_argument(
        "--schema",
        help="Path to the schema SQL file (overrides db/schema.sql).",
    )
    args = parser.parse_args()

    root = repo_root()
    settings = load_settings()

    database_path = args.database or settings.get(
        "database_path", "data/price-tracker.db"
    )
    schema_path = args.schema or root / "db" / "schema.sql"

    if not Path(database_path).is_absolute():
        database_path = root / database_path
    if not Path(schema_path).is_absolute():
        schema_path = root / schema_path

    Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    init_database(database_path, schema_path)
    print(f"Initialized database at {database_path} from {schema_path}")


if __name__ == "__main__":
    main()
