from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.serve import product_page, product_retailer_prices


class TestProductPage(unittest.TestCase):
    def test_product_route_uses_the_shared_template(self):
        response = product_page("amd-ryzen-5-9600x")

        self.assertEqual(Path(response.path).name, "product.html")

    def test_template_contains_all_product_sections(self):
        page_path = Path(__file__).resolve().parents[1] / "web" / "product.html"
        page = page_path.read_text(encoding="utf-8")

        for expected in (
            "Price history",
            "Period low",
            "Period high",
            "Median price",
            "Observations",
            "Where to buy",
            "Latest observations",
            "Other models",
            "src=\"/static/js/product.js\"",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, page)

    def test_retailer_api_marks_excluded_and_mock_observations(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "product-test.db"
            conn = sqlite3.connect(database_path)
            conn.executescript(
                """
                CREATE TABLE retailers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    base_url TEXT NOT NULL
                );
                CREATE TABLE observations (
                    id INTEGER PRIMARY KEY,
                    observed_at TEXT NOT NULL,
                    sku_id TEXT NOT NULL,
                    retailer_id TEXT NOT NULL,
                    price_cents INTEGER NOT NULL,
                    in_stock INTEGER NOT NULL,
                    source_url TEXT NOT NULL
                );
                CREATE TABLE observation_exclusions (
                    observation_id INTEGER PRIMARY KEY,
                    reason TEXT NOT NULL,
                    excluded_at TEXT NOT NULL
                );
                INSERT INTO retailers VALUES
                    ('amazon', 'Amazon', 'https://www.amazon.com'),
                    ('microcenter', 'Micro Center', 'https://www.microcenter.com');
                INSERT INTO observations VALUES
                    (1, '2026-11-24T10:00:00', 'amd-ryzen-5-9600x', 'amazon',
                     22000, 1, 'web/uploads/old-receipt.png'),
                    (2, '2026-11-23T12:00:00', 'amd-ryzen-5-9600x', 'microcenter',
                     15999, 1, 'Nov 23, 2026 baseline snapshot'),
                    (3, '2026-11-24T11:00:00', 'amd-ryzen-5-9600x', 'amazon',
                     10000, 1, 'https://example.com/mock/price');
                INSERT INTO observation_exclusions VALUES
                    (1, 'Old receipt is not a current price', '2026-11-24T12:00:00');
                """
            )
            conn.close()

            with patch("scripts.serve.DB_PATH", database_path):
                result = product_retailer_prices("amd-ryzen-5-9600x")

        by_id = {row["observation_id"]: row for row in result["retailer_prices"]}
        self.assertTrue(by_id[1]["is_excluded"])
        self.assertEqual(by_id[1]["exclusion_reason"], "Old receipt is not a current price")
        self.assertEqual(by_id[2]["source_label"], "Baseline")
        self.assertFalse(by_id[2]["is_excluded"])
        self.assertEqual(
            by_id[2]["product_url"],
            "https://www.microcenter.com/product/682196/amd-ryzen-5-9600x-granite-ridge-am5-390ghz-6-core-boxed-processor-heatsink-not-included",
        )
        self.assertTrue(by_id[3]["is_mock"])


if __name__ == "__main__":
    unittest.main()
