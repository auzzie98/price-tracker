# 03 Data and index rules

## Source of truth

- observations is the source of truth, append only, never overwritten, never edited by hand.
- sku_prices and index_values are derived, stored, and kept. They grow each period, they are not wiped as a routine step.
- Database schema is in `db/schema.sql`. `scripts/init_db.py` must be safe to run twice, and must not delete existing observations.

## sku_prices

- For each SKU and period, median price across in stock retailers, from observations.
- Out of stock listings are ignored for the median.
- If a SKU has no in stock price in a period, it has no sku_prices row for that period. Do not write a zero.

## index_values

- Follow METHODOLOGY.md exactly. Chained, equal weighted, matched model, starting at 100.
- A new SKU is left out until it has its own history. It counts from its second period, through its own change only.
- One row per category per period, with the number of SKUs used.
- Each new period adds one new row per category and leaves old rows alone.

## Rebuilds and revisions

- Rebuild only when the method changes, when a scraping or matching bug produced bad prices, or when the period length changes.
- Rebuild from observations, through sku_prices, then index_values, in order. Use the workflow in `.clinerules/workflows/rebuild-index.md`.
- If a rebuild changes published numbers, the site must say so, with the dates affected and the reason. See METHODOLOGY.md.

## Tests

- `tests/test_index.py` must use the worked example from METHODOLOGY.md, Days 1 to 4, indexes 100.00, 99.00, 97.35, and 95.65. It must pass before any index code is trusted.
- `tests/test_median.py` must cover a median across in stock retailers, an out of stock listing ignored, and a single retailer case.
