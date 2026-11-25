"""Median test. Task 4 implements the median code.

Cases to cover:
- Median across in stock retailers.
- An out of stock listing is ignored.
- A single retailer case returns that price.
"""

import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_tracker.index import build_sku_prices


class TestMedian(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(
            """
            CREATE TABLE skus (
                id TEXT PRIMARY KEY, mpn TEXT NOT NULL, brand TEXT NOT NULL,
                model TEXT NOT NULL, category TEXT NOT NULL, chip TEXT, architecture TEXT
            );
            CREATE TABLE retailers (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, base_url TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                observed_at TEXT NOT NULL, sku_id TEXT NOT NULL, retailer_id TEXT NOT NULL,
                price_cents INTEGER NOT NULL, in_stock INTEGER NOT NULL, source_url TEXT NOT NULL
            );
            CREATE TABLE observation_exclusions (
                observation_id INTEGER PRIMARY KEY,
                reason TEXT NOT NULL,
                excluded_at TEXT NOT NULL
            );
            CREATE TABLE sku_prices (
                sku_id TEXT NOT NULL, period TEXT NOT NULL,
                median_price_cents INTEGER NOT NULL, retailers_used INTEGER NOT NULL,
                PRIMARY KEY (sku_id, period)
            );
            """
        )
        self.conn.execute(
            "INSERT INTO skus VALUES ('sku-1', 'MPN-1', 'Brand', 'Model', 'GPUs', NULL, NULL)"
        )
        self.conn.execute(
            "INSERT INTO retailers VALUES ('r1', 'Retailer 1', 'http://example.com', 1)"
        )
        self.conn.execute(
            "INSERT INTO retailers VALUES ('r2', 'Retailer 2', 'http://example.com', 1)"
        )
        self.conn.execute(
            "INSERT INTO retailers VALUES ('r3', 'Retailer 3', 'http://example.com', 1)"
        )
        self.conn.commit()

    def _insert_observations(self, rows):
        self.conn.executemany(
            "INSERT INTO observations (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        self.conn.commit()

    def _fetch_sku_price(self, sku_id="sku-1", period="2026-01-01"):
        return self.conn.execute(
            "SELECT median_price_cents, retailers_used FROM sku_prices "
            "WHERE sku_id = ? AND period = ?",
            (sku_id, period),
        ).fetchone()

    def test_median_across_in_stock_retailers(self):
        """Three in stock retailers: median of [50000, 60000, 70000] = 60000."""
        self._insert_observations(
            [
                ("2026-01-01T10:00:00", "sku-1", "r1", 50000, 1, "http://example.com/1"),
                ("2026-01-01T10:00:00", "sku-1", "r2", 60000, 1, "http://example.com/2"),
                ("2026-01-01T10:00:00", "sku-1", "r3", 70000, 1, "http://example.com/3"),
            ]
        )
        build_sku_prices(self.conn)
        row = self._fetch_sku_price()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 60000)
        self.assertEqual(row[1], 3)

    def test_out_of_stock_listing_ignored(self):
        """Two in stock, one out of stock: median of [50000, 70000] = 60000."""
        self._insert_observations(
            [
                ("2026-01-01T10:00:00", "sku-1", "r1", 50000, 1, "http://example.com/1"),
                ("2026-01-01T10:00:00", "sku-1", "r2", 65000, 0, "http://example.com/2"),
                ("2026-01-01T10:00:00", "sku-1", "r3", 70000, 1, "http://example.com/3"),
            ]
        )
        build_sku_prices(self.conn)
        row = self._fetch_sku_price()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 60000)
        self.assertEqual(row[1], 2)

    def test_single_retailer(self):
        """One in stock retailer: returns that price."""
        self._insert_observations(
            [
                ("2026-01-01T10:00:00", "sku-1", "r1", 50000, 1, "http://example.com/1"),
            ]
        )
        build_sku_prices(self.conn)
        row = self._fetch_sku_price()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 50000)
        self.assertEqual(row[1], 1)

    def test_mock_and_excluded_observations_do_not_enter_medians(self):
        self._insert_observations(
            [
                ("2026-01-01T10:00:00", "sku-1", "r1", 10000, 1, "https://example.com/mock/1"),
                ("2026-01-01T10:00:00", "sku-1", "r2", 50000, 1, "https://retailer.example/2"),
                ("2026-01-01T10:00:00", "sku-1", "r3", 90000, 1, "web/uploads/old-receipt.png"),
            ]
        )
        receipt_id = self.conn.execute(
            "SELECT id FROM observations WHERE source_url = ?",
            ("web/uploads/old-receipt.png",),
        ).fetchone()[0]
        self.conn.execute(
            "INSERT INTO observation_exclusions VALUES (?, ?, ?)",
            (receipt_id, "Old receipt, not a current price.", "2026-01-02T00:00:00Z"),
        )
        self.conn.commit()

        build_sku_prices(self.conn)

        row = self._fetch_sku_price()
        self.assertEqual(row, (50000, 1))

    def tearDown(self):
        self.conn.close()


if __name__ == "__main__":
    unittest.main()
