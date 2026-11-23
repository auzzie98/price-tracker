# Rebuild index

Use this workflow only when METHODOLOGY.md allows a rebuild, and only after recording the reason in DECISIONS.md.

## When to rebuild

- The formula changes, such as adding weighting.
- A scraping or matching bug produced bad prices. Fix it first, then recompute the affected dates.
- The refresh interval or period length changes.

Do not rebuild as a routine step. In normal operation index_values grows, one new row per category per period.

## Steps

1. Read METHODOLOGY.md, .clinerules/03-data-and-index-rules.md, and the DECISIONS.md row for this rebuild.
2. Back up the database file in data/ before the rebuild, and record the backup name.
3. Rebuild in order: observations, then sku_prices, then index_values. Use `python scripts\build_derived.py --rebuild`.
4. Run `tests/test_index.py` and check the worked example still gives 100.00, 99.00, 97.35, and 95.65 for Days 1 to 4.
5. Compare old and new index_values for the affected dates. If any published number changed, update the methodology page to say so, with the dates affected and the reason.

## Run commands, Windows

```
venv\Scripts\activate
python scripts\build_derived.py --rebuild
python -m unittest discover -s tests -v
```

## Done check

No duplicate rows, the worked example test passes, and any changed published number is noted on the methodology page.
