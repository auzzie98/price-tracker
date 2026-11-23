# Add retailer

Use this workflow only after the check retailer workflow is green for that retailer, and only for one retailer at a time.

## Steps

1. Read TASKS.md for the current retailer task, RETAILER_FEASIBILITY.md for that retailer row, and .clinerules/02-scraping-rules.md.
2. Create one module in `src/price_tracker/scrape/`, named for the retailer, sharing `base.py`. Same input and same output shape as the other scrapers.
3. Add the retailer to `config/retailers.yaml`, with enabled true, only if the feasibility row says it passed.
4. Scrape one exact product page, once, and check that one observation is written, with the right SKU, retailer, price in cents, in stock flag, and source URL.
5. Run `python scripts\scrape_once.py` for that retailer only, then `python scripts\build_derived.py`, and check the derived rows.

## Run commands, Windows

```
venv\Scripts\activate
python scripts\scrape_once.py --retailer newegg
python scripts\build_derived.py
python -m unittest discover -s tests -v
```

Replace newegg with the retailer id from config/retailers.yaml.

## Done check

One observation, one sku_prices row, and no duplicate rows on a rerun. If the scraper cannot find a price, it logs not found and writes no observation.
