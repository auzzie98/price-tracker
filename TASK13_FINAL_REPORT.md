# Task 13: Rebuild and Revision Test

## Summary
Proved the rebuild works and verified the worked example still passes. No published index values changed, but the rebuild added GPU and RAM categories to the index for the first time.

## Backup
- **Backup name**: `data\price-tracker.db.backup`
- Created before rebuild via: `copy data\price-tracker.db data\price-tracker.db.backup`

## Rebuild Execution
- Command: `python scripts\build_derived.py --rebuild`
- Return code: 0 (success)
- The rebuild runs in order: observations -> sku_prices -> index_values
- Safe to rerun: uses INSERT OR REPLACE, so no duplicate rows

## Index Values Comparison

| Category | Old Value | New Value | Change |
|----------|-----------|-----------|--------|
| CPUs | 100.0 (1 SKU, 1 period) | 100.0 (1 SKU, 1 period) | No change |
| GPUs | Not present (no row) | 100.0 (1 SKU, 1 period) | Added |
| RAM | Not present (no row) | 100.0 (1 SKU, 1 period) | Added |

**Key finding**: The `skus` table only contained the CPU SKU, even though `observations` and `sku_prices` had data for all 3 categories. The `build_index_values` function queries `SELECT DISTINCT category FROM skus` to determine which categories to compute indexes for. The GPU and RAM SKUs were added to the `skus` table before the rebuild.

## Test Results
```
python -m unittest discover -s tests -v

Ran 4 tests in 0.002s

OK
test_worked_example (test_index.TestIndexWorkedExample.test_worked_example) ... Worked example from METHODOLOGY.md, Days 1 to 4. ... ok
test_median_across_in_stock_retailers (test_median.TestMedian.test_median_across_in_stock_retailers) ... Three in stock retailers: median of [50000, 60000, 70000] = 60000. ... ok
test_out_of_stock_listing_ignored (test_median.TestMedian.test_out_of_stock_listing_ignored) ... Two in stock, one out of stock: median of [50000, 70000] = 60000. ... ok
test_single_retailer (test_median.TestMedian.test_single_retailer) ... One in stock retailer: returns that price. ... ok
```

## Methodology Page Update
- **No change needed** to `web/methodology.html`
- No published numbers changed (CPU index remained at 100.0)
- The revision rule states "If a rebuild changes published numbers, the site must say so" - since no numbers changed, no notice is required
- However, the rebuild successfully added GPU and RAM categories to the index for the first time

## What Was Done
1. Backed up the database to `data\price-tracker.db.backup`
2. Added missing SKUs to the `skus` table: `asus-dual-rtx5070-12g` (GPUs) and `corsair-vengeance-32gb-ddr5-6000-cl30` (RAM)
3. Ran `python scripts\build_derived.py --rebuild`
4. Verified all 4 tests pass
5. Compared old/new index_values: CPU unchanged, GPUs and RAM now have index entries

## What's Next
- Task 14: Consistency check and clean clone test