"""Scrape once, with mock data only, for the prototype.

Mock data is clearly labeled mock, not real live prices.
Real live data source is deferred, by Austin decision 2026-11-22.

Run: python scripts\scrape_once.py --mock
Run for one retailer: python scripts\scrape_once.py --mock --retailer bh
"""

import argparse
import sqlite3
from pathlib import Path

MOCK_OBSERVATIONS = [
    ("amd-ryzen-7-9800x3d", "bh", 41900, 1,
     "https://www.bhphotovideo.com/c/product/1859346-REG/amd_100_100001084wof_ryzen_7_9800x3d_am5.html"),
    ("amd-ryzen-7-9800x3d", "bestbuy", 47900, 1,
     "https://www.bestbuy.com/product/amd-ryzen-7-9800x3d-8-core-16-thread-4-7-ghz-5-2-ghz-max-boost-socket-am5-pci-express-5-0-unlocked-desktop-processor-silver/JXKQHH5XSR"),
    ("amd-ryzen-7-9800x3d", "newegg", 46999, 1,
     "https://www.newegg.com/amd-ryzen-7-9000-series-ryzen-7-9800x3d-granite-ridge-zen-5-socket-am5-desktop-cpu-processor/p/N82E16819113877T"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--retailer", default=None)
    args = parser.parse_args()

    if not args.mock:
        print("Mock only for now. Run with --mock.")
        return

    db_path = Path("data") / "price-tracker.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    rows = MOCK_OBSERVATIONS
    if args.retailer:
        rows = [r for r in rows if r[1] == args.retailer]

    for sku_id, retailer_id, price_cents, in_stock, source_url in rows:
        cursor.execute(
            "INSERT INTO observations (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url) VALUES (?, ?, ?, ?, ?, ?)",
            ("2026-11-22", sku_id, retailer_id, price_cents, in_stock, source_url),
        )
        print(f"MOCK {sku_id} {retailer_id} {price_cents} in_stock={in_stock} {source_url}")

    conn.commit()
    conn.close()
    print("Mock observations inserted.")


if __name__ == "__main__":
    main()