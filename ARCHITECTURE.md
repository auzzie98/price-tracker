# Architecture

## Overview

Prototype, local first. No paid services in v1. No deployment in v1 until Azure for Students is verified and DECISIONS.md records it.

Data flows in one direction:

Scrapers write observations. A job builds sku_prices from observations. A second job builds index_values from sku_prices. The website reads sku_prices and index_values only, never raw observations directly for charts.

```
retailer pages
  -> scrapers, one module per retailer
  -> observations, append only
  -> build sku_prices, median per SKU per period
  -> build index_values, chained index per category per period
  -> API, JSON
  -> website, Lightweight Charts
```

## Tech stack

- Python 3.12 on Windows, virtual environment
- SQLite, `db/schema.sql` as the source of truth
- Requests and BeautifulSoup for scrapers, no headless browser in v1
- FastAPI and Uvicorn for the local API
- Plain HTML, CSS, and JavaScript, no build step, no Node, no framework
- TradingView Lightweight Charts, Apache 2.0, from CDN

## Folder structure

```
price-tracker/
  README.md
  PROJECT_PLAN.md
  TASKS.md
  AGENTS.md
  METHODOLOGY.md
  ARCHITECTURE.md
  DECISIONS.md
  RETAILER_FEASIBILITY.md
  requirements.txt
  .gitignore
  .clinerules/
    00-read-first.md
    01-coding-standards.md
    02-scraping-rules.md
    03-data-and-index-rules.md
    04-frontend-rules.md
    workflows/
      start-prototype.md
      check-retailer.md
      add-retailer.md
      add-product.md
      rebuild-index.md
      run-checks.md
  config/
    settings.yaml
    retailers.yaml
    products.yaml
  db/
    schema.sql
  src/price_tracker/
    __init__.py
    config.py
    db.py
    index.py
    scrape/
      __init__.py
      base.py
      newegg.py
      bestbuy.py
      microcenter.py
      bh.py
      amazon.py
  scripts/
    init_db.py
    scrape_once.py
    build_derived.py
    serve.py
  web/
    index.html
    category.html
    product.html
    methodology.html
    static/css/style.css
    static/js/chart.js
    static/js/api.js
  tests/
    test_index.py
    test_median.py
  data/
    .gitkeep
```

Rules for the structure:
- `src/price_tracker/` holds library code only. No script in `src/` reads the command line or writes files on import.
- `scripts/` holds the runnable entry points only. Each script is thin, it parses arguments and calls library code.
- `config/` holds settings, retailers, and products. Code reads config, it does not hard code retailer URLs, product lists, or refresh intervals.
- `web/` holds static files only. No server code in `web/`.
- `data/` holds the local database only. It is ignored by git. Never edit it by hand.
- `tests/` holds checks that run with the Python standard library only.

## Database

SQLite, one file: `data/price-tracker.db`. Schema is in `db/schema.sql`. `scripts/init_db.py` creates the file from that schema. It must be safe to run twice, it must not delete existing observations.

Tables, from METHODOLOGY.md:
- observations: timestamp, SKU, retailer, price, in stock flag. Append only, never overwritten. This is the source of truth.
- sku_prices: SKU, period, median price. Derived, rebuildable.
- index_values: category, period, index value, SKUs used. Derived, rebuildable, kept and grown each period.

Also in the schema, kept small in v1:
- skus: SKU id, manufacturer part number, brand, model, category, chip, architecture.
- retailers: retailer id, name, base URL.
- sku_retailer_urls: SKU id, retailer id, product page URL, active flag.
- page_views: product page views, anonymous counter, for the later most viewed list. Count only, no user data. May be empty in the prototype.

Indexes: observations by SKU and timestamp, sku_prices by SKU and period, index_values by category and period. No other indexes in v1 unless a query is slow and the task notes it.

## Config files

`config/settings.yaml`: refresh interval in hours, provisional default 6, period length, user agent string, request delay in seconds, database path, API host and port. One place for all run time settings.
`config/retailers.yaml`: one entry per retailer, with name, base URL, robots.txt URL, terms URL, enabled flag, and notes from RETAILER_FEASIBILITY.md.
`config/products.yaml`: hand picked starting list only. One entry per SKU, with manufacturer part number, brand, model, category, chip, and the exact page URL at each retailer that lists it. No searching or guessing in v1.

## Scrapers

One module per retailer in `src/price_tracker/scrape/`. All scrapers share `base.py`:
- Same input: a SKU and a product page URL from config.
- Same output: an observation, timestamp, SKU, retailer, price, in stock flag, plus source URL.
- Same behavior: one page at a time, a short delay between requests, a clear user agent that names this project, polite errors, no retry storm.
- If a page is blocked, or shows a CAPTCHA, the scraper stops for that retailer, logs the result, and returns no observation. It does not work around the block.
- Price parsing lives in the retailer module only, since each site puts the price in a different place. See RETAILER_FEASIBILITY.md for where the price lives per retailer.

## Derived jobs

`scripts/build_derived.py` runs two steps, in order:
1. Build sku_prices: for each SKU and period, median price across in stock retailers, from observations.
2. Build index_values: for each category and period, chained equal weighted index from sku_prices, using METHODOLOGY.md, starting at 100, skipping a new SKU until its second period.

Both steps must be safe to rerun. Rerunning with no new observations must not duplicate rows. Rebuilding after a method change must follow the revision rule in METHODOLOGY.md.

## API, local only in v1

FastAPI app in `scripts/serve.py`, or in `src/price_tracker/` with a thin script wrapper. Keep it thin in v1.

Endpoints, all JSON, all read only in v1:
- `GET /api/indexes` : list of categories, with current index value and percent change.
- `GET /api/indexes/{category}` : index_values rows for one category, with period, index value, and SKUs used.
- `GET /api/products` : list of tracked SKUs, with brand, model, category, and current median price.
- `GET /api/products/{sku}` : sku_prices rows for one SKU, with period, median price, and retailers used.
- `GET /api/movers?range=1d` : biggest movers, largest price drops and rises, from sku_prices. Range is 1d or 1w in the prototype.
- `GET /api/health` : database file exists, row counts for observations, sku_prices, and index_values.

No write endpoints in v1. No auth in v1, since the prototype runs locally only.

## Website

Plain static pages in `web/`, served by the same FastAPI app in v1, or by a static file server during prototyping. No framework, no build step.

- `index.html`: index tiles on top, then the biggest movers list, with a 1D and 1W toggle. Room left in the layout for the cheapest and most viewed lists later.
- `category.html`: full index chart for one category, plus the list of tracked products in it.
- `product.html`: dollar price chart for one exact product, plus which retailers its price comes from.
- `methodology.html`: how the index works, which sites are scraped, the v1 limits, and the cold start. Copy from METHODOLOGY.md, in plain words.

Charts: one chart component in `web/static/js/chart.js`, using TradingView Lightweight Charts, line and area series. The same component draws dollar charts and index charts. The only difference is the vertical axis label and the data source. Time toggles are 1D, 1W, 1M, and 1Y, filtering the same series, not a different chart type.

Styling: strict black and white in v1, plain and readable, no color coding that carries meaning alone. Charts use a single dark line on a white background, with a light grid.

## Tests

Python standard library only, run with:

```
python -m unittest discover -s tests -v
```

- `tests/test_index.py`: the worked example from METHODOLOGY.md, Days 1 to 4, indexes 100.00, 99.00, 97.35, and 95.65. This test must pass before any index code is trusted.
- `tests/test_median.py`: median across in stock retailers, including an out of stock listing ignored, and a single retailer case.

No test invents a price. Tests use the worked example, or small made up numbers labeled as test data only.

## What is not in v1

- No headless browser, no paid data feed, no affiliate link.
- No user accounts, no saved lists, no analytics, no ads.
- No deployment, no Azure setup, until DECISIONS.md records it.
- No weighting, no quality adjustment, no backfill.
