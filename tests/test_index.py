"""Index test, from the worked example in METHODOLOGY.md.

Days 1 to 4, indexes 100.00, 99.00, 97.35, and 95.65.
Do not change these numbers. They are the source of truth for the test.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_tracker.index import build_index_values, compute_index


class TestIndexWorkedExample(unittest.TestCase):
    def test_worked_example(self):
        """Worked example from METHODOLOGY.md, Days 1 to 4.

        Median price per SKU per day (dollars):
            SKU | Day 1 | Day 2 | Day 3 | Day 4
            A   | 500   | 490   | 490   | 480.20
            B   | 600   | 600   | 570   | 570
            C   | 700   | 693   | 693   | 693
            D   | none  | none  | 900   | 855

        Expected indexes: 100.00, 99.00, 97.35, 95.65.
        SKU D is new on Day 3 (skipped), counts on Day 4.
        """
        period_prices = {
            "Day 1": {"A": 500.0, "B": 600.0, "C": 700.0},
            "Day 2": {"A": 490.0, "B": 600.0, "C": 693.0},
            "Day 3": {"A": 490.0, "B": 570.0, "C": 693.0, "D": 900.0},
            "Day 4": {"A": 480.20, "B": 570.0, "C": 693.0, "D": 855.0},
        }
        results = compute_index(period_prices)

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0], ("Day 1", 100.0, 3))
        self.assertEqual(results[1], ("Day 2", 99.0, 3))
        self.assertEqual(results[2], ("Day 3", 97.35, 3))
        self.assertEqual(results[3], ("Day 4", 95.65, 4))


class TestIndexBaseline(unittest.TestCase):
    def setUp(self):
        import sqlite3

        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(
            """
            CREATE TABLE skus (id TEXT PRIMARY KEY, category TEXT NOT NULL);
            CREATE TABLE observations (
                id INTEGER PRIMARY KEY,
                observed_at TEXT NOT NULL,
                sku_id TEXT NOT NULL,
                in_stock INTEGER NOT NULL,
                source_url TEXT NOT NULL
            );
            CREATE TABLE observation_exclusions (
                observation_id INTEGER PRIMARY KEY,
                reason TEXT NOT NULL,
                excluded_at TEXT NOT NULL
            );
            CREATE TABLE sku_prices (
                sku_id TEXT NOT NULL,
                period TEXT NOT NULL,
                median_price_cents INTEGER NOT NULL,
                retailers_used INTEGER NOT NULL
            );
            CREATE TABLE index_values (
                category TEXT NOT NULL,
                period TEXT NOT NULL,
                index_value REAL NOT NULL,
                skus_used INTEGER NOT NULL,
                PRIMARY KEY (category, period)
            );
            """
        )
        self.conn.execute("INSERT INTO skus VALUES ('gpu-1', 'GPUs')")
        self.conn.executemany(
            "INSERT INTO sku_prices VALUES (?, ?, ?, ?)",
            [
                ("gpu-1", "2026-11-22", 50000, 1),
                ("gpu-1", "2026-11-23", 100000, 1),
                ("gpu-1", "2026-11-24", 200000, 1),
                ("gpu-1", "2026-11-25", 300000, 1),
            ],
        )
        self.conn.executemany(
            "INSERT INTO observations VALUES (?, ?, ?, ?, ?)",
            [
                (1, "2026-11-22T10:00:00", "gpu-1", 1, "https://example.com/mock/1"),
                (2, "2026-11-23T10:00:00", "gpu-1", 1, "https://retailer.example/gpu"),
                (3, "2026-11-24T10:00:00", "gpu-1", 1, "web/uploads/old-receipt.png"),
            ],
        )
        self.conn.execute(
            "INSERT INTO observation_exclusions VALUES (3, ?, ?)",
            ("Old receipt, not a current market price.", "2026-11-24T12:00:00Z"),
        )
        self.conn.commit()

    def test_build_index_uses_configured_baseline_and_valid_observations(self):
        products = [{"id": "gpu-1", "category": "GPUs"}]
        settings = {"index_baseline_period": "2026-11-23"}
        with patch("price_tracker.config.load_products", return_value=products), patch(
            "price_tracker.config.load_settings", return_value=settings
        ):
            build_index_values(self.conn)

        rows = self.conn.execute(
            "SELECT period, index_value, skus_used FROM index_values "
            "WHERE category = 'GPUs' ORDER BY period"
        ).fetchall()
        self.assertEqual(rows, [("2026-11-23", 100.0, 1)])

    def test_category_without_baseline_does_not_start_later(self):
        self.conn.execute(
            "DELETE FROM sku_prices WHERE period = '2026-11-23'"
        )
        self.conn.execute(
            "INSERT INTO observations VALUES (?, ?, ?, ?, ?)",
            (4, "2026-11-24T10:00:00", "gpu-1", 1, "https://retailer.example/gpu"),
        )
        self.conn.commit()
        products = [{"id": "gpu-1", "category": "GPUs"}]
        settings = {"index_baseline_period": "2026-11-23"}
        with patch("price_tracker.config.load_products", return_value=products), patch(
            "price_tracker.config.load_settings", return_value=settings
        ):
            build_index_values(self.conn)

        rows = self.conn.execute(
            "SELECT period, index_value FROM index_values WHERE category = 'GPUs'"
        ).fetchall()
        self.assertEqual(rows, [])

    def tearDown(self):
        self.conn.close()


if __name__ == "__main__":
    unittest.main()
