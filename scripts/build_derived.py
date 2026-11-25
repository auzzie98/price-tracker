"""Build sku_prices, then index_values, from observations.

Run: python scripts\build_derived.py
Must be safe to rerun. Must not duplicate rows.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_tracker.config import load_settings, repo_root
from price_tracker.db import connect, init_database
from price_tracker.index import build_sku_prices, build_index_values


def main() -> None:
    parser = argparse.ArgumentParser(description="Build derived price and index data.")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Clear and rebuild sku_prices and index_values from observations.",
    )
    parser.add_argument(
        "--exclude-observation",
        action="append",
        type=int,
        default=[],
        metavar="ID",
        help="Keep this raw observation out of derived prices. May be repeated.",
    )
    parser.add_argument(
        "--exclusion-reason",
        help="Required reason when excluding one or more observations.",
    )
    args = parser.parse_args()
    if args.exclude_observation and not args.rebuild:
        parser.error("--exclude-observation requires --rebuild")
    if args.exclude_observation and not args.exclusion_reason:
        parser.error("--exclusion-reason is required when excluding observations")

    root = repo_root()
    settings = load_settings()
    database_path = settings.get("database_path", "data/price-tracker.db")
    if not Path(database_path).is_absolute():
        database_path = root / database_path

    schema_path = root / "db" / "schema.sql"
    init_database(database_path, schema_path)

    conn = connect(database_path)
    try:
        if args.exclude_observation:
            excluded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            for observation_id in args.exclude_observation:
                exists = conn.execute(
                    "SELECT 1 FROM observations WHERE id = ?", (observation_id,)
                ).fetchone()
                if not exists:
                    raise ValueError(
                        f"Observation {observation_id} does not exist."
                    )
                conn.execute(
                    """
                    INSERT OR REPLACE INTO observation_exclusions
                        (observation_id, reason, excluded_at)
                    VALUES (?, ?, ?)
                    """,
                    (observation_id, args.exclusion_reason, excluded_at),
                )

        if args.rebuild:
            conn.execute("DELETE FROM sku_prices")
            conn.execute("DELETE FROM index_values")
            conn.commit()

        build_sku_prices(conn)
        build_index_values(conn)
        print("Built sku_prices and index_values from eligible observations.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
