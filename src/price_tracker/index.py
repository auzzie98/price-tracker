"""Index math: median prices per SKU per period, and chained equal weighted index.

Follows METHODOLOGY.md exactly:
- Median price per SKU per period, from in stock observations only.
- Chained, equal weighted, matched model index starting at 100.
- A new SKU is left out until its second period, then counts through its own change only.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict


def median_price(prices: list[int]) -> int:
    """Return the median price (in cents) of a list of prices."""
    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    mid = n // 2
    if n % 2 == 1:
        return sorted_prices[mid]
    return (sorted_prices[mid - 1] + sorted_prices[mid]) // 2


def build_sku_prices(conn: sqlite3.Connection) -> None:
    """Build sku_prices from observations: median per SKU per period, in stock only.

    Out of stock observations are ignored. If a SKU has no in stock price in a
    period, it gets no sku_prices row for that period (no zero is written).
    Safe to rerun: uses INSERT OR REPLACE, so no duplicate rows.
    """
    rows = conn.execute(
        """
        SELECT sku_id, substr(observed_at, 1, 10) AS period, price_cents
        FROM observations
        WHERE in_stock = 1
        ORDER BY sku_id, period
        """
    ).fetchall()

    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for sku_id, period, price_cents in rows:
        grouped[(sku_id, period)].append(price_cents)

    for (sku_id, period), prices in sorted(grouped.items()):
        med = median_price(prices)
        conn.execute(
            """
            INSERT OR REPLACE INTO sku_prices (sku_id, period, median_price_cents, retailers_used)
            VALUES (?, ?, ?, ?)
            """,
            (sku_id, period, med, len(prices)),
        )
    conn.commit()


def compute_index(
    period_prices: dict[str, dict[str, float]]
) -> list[tuple[str, float, int]]:
    """Compute chained equal weighted index from period prices.

    Args:
        period_prices: {period: {sku_id: price}}

    Returns:
        List of (period, index_value, skus_used), one per period.
    """
    periods = sorted(period_prices.keys())
    if not periods:
        return []

    results: list[tuple[str, float, int]] = []
    prev_index = 100.0

    # First period: index is 100.
    first = periods[0]
    results.append((first, 100.0, len(period_prices[first])))

    # Subsequent periods: chained from previous period.
    for i in range(1, len(periods)):
        prev = periods[i - 1]
        curr = periods[i]

        # Only SKUs priced in both periods count (matched model).
        common = set(period_prices[prev].keys()) & set(period_prices[curr].keys())

        if not common:
            results.append((curr, prev_index, 0))
            continue

        relatives = [
            period_prices[curr][sku] / period_prices[prev][sku] for sku in common
        ]
        avg_relative = sum(relatives) / len(relatives)
        curr_index = round(prev_index * avg_relative, 2)
        results.append((curr, curr_index, len(common)))
        prev_index = curr_index

    return results


def build_index_values(conn: sqlite3.Connection) -> None:
    """Build index_values from sku_prices: chained index per category per period.

    Safe to rerun: uses INSERT OR REPLACE, so no duplicate rows.
    Each new period adds one row per category and leaves old rows alone.
    """
    from price_tracker.config import load_products

    configured = {
        product["id"]: product["category"]
        for product in load_products()
    }
    categories = ["GPUs", "CPUs", "RAM"]

    for category in categories:
        skus = [
            r[0]
            for r in conn.execute(
                "SELECT id FROM skus WHERE category = ?", (category,)
            ).fetchall()
            if r[0] in configured
        ]

        if not skus:
            continue

        placeholders = ",".join("?" for _ in skus)
        rows = conn.execute(
            f"""
            SELECT sku_id, period, median_price_cents
            FROM sku_prices
            WHERE sku_id IN ({placeholders})
            ORDER BY sku_id, period
            """,
            skus,
        ).fetchall()

        period_prices: dict[str, dict[str, float]] = defaultdict(dict)
        for sku_id, period, price_cents in rows:
            period_prices[period][sku_id] = float(price_cents)

        index_rows = compute_index(period_prices)

        for period, index_value, skus_used in index_rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO index_values (category, period, index_value, skus_used)
                VALUES (?, ?, ?, ?)
                """,
                (category, period, index_value, skus_used),
            )
    conn.commit()
