# Price Tracker

An open source website that tracks computer part prices over time and draws them like a stock chart, so anyone who can read a chart can see at a glance whether prices are rising or falling.

Who it is for: researchers and price watchers, with GPU buyers as the core audience and RAM and CPU buyers as the second wave.

Long term goal: a credible public reference for hardware price inflation that a team or company could take over and turn into something economists cite.

## What v1 does

- Tracks GPUs, CPUs, and RAM, from a hand picked list of exact products
- Shows a stock style line chart for each product in dollars, and for each category as an index starting at 100
- Front page with index tiles and a biggest movers list, category pages, product pages, and a methodology page
- Scrapes prices from retailers, shows every source publicly, and keeps every raw observation
- No accounts, no affiliate links, no paid data feeds, no ads in v1

## What v1 does not do

- Other components, user accounts, saved lists, affiliate links, paid feeds
- Quality adjustment, weighting, or economist grade methodology
- Backfilled history. Charts start at launch and history builds up honestly
- Ads and premium price alerts. Those are for a later release

## Tech stack, chosen for the prototype

- Python 3.12 on Windows, with a virtual environment
- SQLite, one local database file, with `db/schema.sql` as the source of truth
- Requests and BeautifulSoup for scrapers, one module per retailer, no headless browser in v1
- FastAPI and Uvicorn for the local API, plain HTML, CSS, and JavaScript for the site, no build step and no Node
- TradingView Lightweight Charts, Apache 2.0, loaded from CDN, for line and area time series charts
- Cline in VS Code, with Nemotron 3.5 Super VL first. See `AGENTS.md` and `.clinerules/` for how the coding agent works in this repo

## Quick start, Windows

Open a terminal in the repo root, then run these commands one at a time.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts\init_db.py
python scripts\scrape_once.py
python scripts\build_derived.py
python scripts\serve.py
```

Then open `http://127.0.0.1:8000` in a browser.

Note: the scripts above are starter tasks in `TASKS.md`. Task 1 creates them. Until Task 1 is done, this quick start lists the intended commands, not files that already exist.

## Repo layout

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
  .clinerules/
    00-read-first.md
    01-coding-standards.md
    02-scraping-rules.md
    03-data-and-index-rules.md
    04-frontend-rules.md
    workflows/
  config/
    settings.yaml
    retailers.yaml
    products.yaml
  db/
    schema.sql
  src/price_tracker/
  scripts/
  web/
  tests/
  data/
```

## How to work in this repo

1. Read `TASKS.md` first. Do one task at a time, in order, and check it off only when its check is green.
2. Read `AGENTS.md` and `.clinerules/00-read-first.md` before changing code. Cline reads those files automatically.
3. Read `PROJECT_PLAN.md` for scope, `METHODOLOGY.md` for the index math, and `ARCHITECTURE.md` for how the parts fit together.
4. Never edit `data/` by hand. Observations are append only. Derived tables are rebuilt from observations.
5. Never put API keys, passwords, or private data in the repo, in prompts, or in scraped output. See `.gitignore`.

## Data rules, short version

- New products only.
- Only listings sold by the retailer itself, or fulfilled by it. Third party marketplace sellers are skipped in v1.
- Products are hand picked, matched by manufacturer part number, and recorded once in `config/products.yaml` with the exact page URL at each retailer.
- One observation is one scraped data point: timestamp, SKU, retailer, price, in stock flag.
- A SKU price is the median across in stock retailers per period.
- The index is chained, equal weighted, matched model, starting at 100. See `METHODOLOGY.md` for the worked example.

## Retailers in v1 testing

Amazon, Newegg, Micro Center, Best Buy, and B and H. Amazon blocks scrapers aggressively, so v1 must still work if Amazon is dropped. See `RETAILER_FEASIBILITY.md` and `config/retailers.yaml`.

## License and hosting, still open

License is permissive, MIT or Apache 2.0, final pick pending during prototyping. Hosting is Azure for Students, terms to verify once it is needed. Do not add a license file or deploy anything until those two are decided in `DECISIONS.md`.

## Status

Pre draft planning is done. The final plan, the agent instructions, and the starter tasks are in this repo. Prototyping starts at Task 1 in `TASKS.md`.
