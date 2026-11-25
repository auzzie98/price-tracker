import sqlite3
import unittest

from scripts.serve import home_price_points


class TestHomePricePoints(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(
            """
            CREATE TABLE sku_prices (
                sku_id TEXT NOT NULL,
                period TEXT NOT NULL,
                median_price_cents INTEGER NOT NULL,
                retailers_used INTEGER NOT NULL
            );
            CREATE TABLE observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            """
        )

    def test_includes_baseline_and_direct_observations_only(self):
        points = [
            ("2026-11-22", 47000, 1, "https://example.com/mock/model"),
            ("2026-11-23", 41900, 1, "Nov 23, 2026 baseline snapshot"),
            ("2026-11-24", 22000, 1, "web/uploads/old-receipt.png"),
            ("2026-11-24", 37999, 1, "https://retailer.example/product"),
        ]
        for period, price, retailers_used, source_url in points:
            sku_id = (
                "direct-sku"
                if source_url.startswith("https://retailer")
                else "test-sku"
            )
            self.conn.execute(
                "INSERT INTO sku_prices VALUES (?, ?, ?, ?)",
                (
                    sku_id,
                    period,
                    price,
                    retailers_used,
                ),
            )
            cursor = self.conn.execute(
                "INSERT INTO observations "
                "(observed_at, sku_id, in_stock, source_url) VALUES (?, ?, ?, ?)",
                (
                    period + "T12:00:00",
                    sku_id,
                    1,
                    source_url,
                ),
            )
            if source_url == "web/uploads/old-receipt.png":
                self.conn.execute(
                    "INSERT INTO observation_exclusions VALUES (?, ?, ?)",
                    (cursor.lastrowid, "Receipt is not a current market price.", period),
                )
        self.conn.commit()

        baseline = home_price_points(self.conn, "test-sku")
        direct = home_price_points(self.conn, "direct-sku")

        self.assertEqual(
            [(point["period"], point["price_cents"]) for point in baseline],
            [("2026-11-23", 41900)],
        )
        self.assertEqual(
            [(point["period"], point["price_cents"]) for point in direct],
            [("2026-11-24", 37999)],
        )

    def test_returns_no_points_without_a_matching_observation(self):
        self.conn.execute(
            "INSERT INTO sku_prices VALUES (?, ?, ?, ?)",
            ("test-sku", "2026-11-24", 22000, 1),
        )
        self.conn.commit()

        self.assertEqual(home_price_points(self.conn, "test-sku"), [])

    def tearDown(self):
        self.conn.close()


if __name__ == "__main__":
    unittest.main()
