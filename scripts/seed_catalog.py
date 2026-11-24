"""Seed the Nov 23, 2026 baseline catalog and clean retailer observations."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_tracker.config import load_products, load_retailers, repo_root
from price_tracker.db import connect, init_database


BASELINES = {
    "msi-rtx-5060-ventus-2x-oc": ("newegg", 51999),
    "gigabyte-rtx-5060-ti-windforce-oc-16gb": ("newegg", 82999),
    "msi-rtx-5070-ventus-2x-oc": ("msi", 89999),
    "gigabyte-rtx-5070-ti-gaming-oc-16gb": ("bestbuy", 149999),
    "sapphire-rx-9060-xt-pulse-16gb": ("newegg", 74999),
    "sapphire-rx-9060-xt-pulse-8gb": ("newegg", 59999),
    "sapphire-rx-9070-xt-pulse": ("newegg", 104999),
    "asrock-arc-b580-challenger-oc": ("microcenter", 35999),
    "asrock-arc-b570-challenger-oc": ("newegg", 28999),
    "amd-ryzen-7-9800x3d": ("bh", 41900),
    "amd-ryzen-5-7600x": ("microcenter", 14999),
    "intel-core-i7-14700k": ("bh", 32999),
    "amd-ryzen-5-9600x": ("microcenter", 15999),
    "amd-ryzen-7-9700x": ("microcenter", 24999),
    "amd-ryzen-9-9900x": ("microcenter", 29999),
    "amd-ryzen-9-9950x": ("bh", 49999),
    "intel-core-i5-14600k": ("bh", 24995),
    "intel-core-ultra-7-265k": ("microcenter", 28999),
    "intel-core-ultra-9-285k": ("bh", 39999),
    "corsair-vengeance-32gb-ddr5-6000-cl30": ("bh", 64399),
    "corsair-vengeance-16gb-ddr5-6000-cl36": ("bestbuy", 31799),
    "gskill-ripjaws-s5-32gb-ddr5-6000-cl30": ("bestbuy", 72099),
    "corsair-dominator-platinum-rgb-32gb-ddr5-6400-cl32": ("newegg", 66999),
    "gskill-trident-z5-rgb-64gb-ddr5-6000-cl36": ("bestbuy", 138635),
    "teamgroup-t-force-delta-rgb-32gb-ddr5-6000-cl38": ("newegg", 50999),
    "crucial-pro-32gb-ddr5-5600-cl46": ("bestbuy", 54999),
}


def main() -> None:
    root = repo_root()
    database_path = root / "data" / "price-tracker.db"
    init_database(database_path, root / "db" / "schema.sql")
    conn = connect(database_path)
    try:
        for retailer in load_retailers():
            conn.execute(
                """INSERT OR IGNORE INTO retailers
                   (id, name, base_url, enabled) VALUES (?, ?, ?, ?)""",
                (
                    retailer["id"],
                    retailer["name"],
                    retailer["base_url"],
                    1 if retailer.get("enabled", True) else 0,
                ),
            )

        for product in load_products():
            conn.execute(
                """INSERT OR IGNORE INTO skus
                   (id, mpn, brand, model, category, chip, architecture)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    product["id"],
                    product["mpn"],
                    product["brand"],
                    product["model"],
                    product["category"],
                    product["chip"],
                    product["architecture"],
                ),
            )
            for retailer_id, url in product["urls"].items():
                if url:
                    conn.execute(
                        """INSERT OR IGNORE INTO sku_retailer_urls
                           (sku_id, retailer_id, url, active) VALUES (?, ?, ?, 1)""",
                        (product["id"], retailer_id, url),
                    )

        for model_id, (retailer_id, price_cents) in BASELINES.items():
            source_url = "Nov 23, 2026 baseline snapshot"
            exists = conn.execute(
                """SELECT 1 FROM observations
                   WHERE substr(observed_at, 1, 10) = '2026-11-23'
                     AND sku_id = ? AND retailer_id = ? AND price_cents = ?""",
                (model_id, retailer_id, price_cents),
            ).fetchone()
            if not exists:
                conn.execute(
                    """INSERT INTO observations
                       (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url)
                       VALUES (?, ?, ?, ?, 1, ?)""",
                    ("2026-11-23T12:00:00", model_id, retailer_id, price_cents, source_url),
                )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
