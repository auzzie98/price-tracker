# AGENTS.md

This file is read by Cline and by other coding agents. It is the project wide instruction file. Cline specific rules live in `.clinerules/`. If they disagree, `.clinerules/00-read-first.md` wins for order of work, and this file wins for project facts.

## Project, in one paragraph

Price Tracker is an open source website that tracks computer part prices over time and draws them like a stock chart. v1 tracks GPUs, CPUs, and RAM, from a hand picked list of exact products, scraped from retailers, with sources shown publicly. No accounts, no affiliate links, no paid data feeds, no ads in v1. See README.md, PROJECT_PLAN.md, and METHODOLOGY.md.

## How to work here

- Work from TASKS.md, one task at a time, in order. Do not skip ahead. Do not start a task until the previous task check is green.
- Read `.clinerules/00-read-first.md` before any code change. It lists the files to read first for each kind of task.
- Small steps only. One file or one small change per edit, then run the check for that task. If a check fails, fix it before moving on.
- Never invent a price, a retailer result, a license, or a hosting fact. If a fact is not in the repo or in a page you opened, mark it as to check.
- Never edit `data/` by hand. Observations are append only. Derived tables are rebuilt from observations.
- Never commit a database file, an API key, a password, or a private file. See `.gitignore`.
- Use plain words in user facing copy. No clever claim style titles. Headings are plain and literal.
- Do not use em dashes or arrow characters in docs, code comments, or user facing copy. Use commas, periods, or plain hyphens.

## Terms, use them exactly

- SKU: one exact product from one manufacturer, matched by manufacturer part number. Example: ASUS Dual RTX 5070 12GB, DUAL-RTX5070-12G.
- Chip: the silicon, such as RTX 5070. Architecture: the generation, such as Blackwell.
- Retailer: a store listing a SKU.
- Observation: one scraped data point, timestamp, SKU, retailer, price, in stock flag.
- sku_prices: median price per SKU per period, from in stock listings.
- index_values: one row per category per period, with the number of SKUs used.
- Category: All GPUs, All CPUs, or All RAM in v1.

## Tech stack

- Python 3.12 on Windows, virtual environment, `python`, activate with `venv\Scripts\activate`
- SQLite, schema in `db/schema.sql`
- Requests and BeautifulSoup for scrapers, one module per retailer, no headless browser in v1
- FastAPI and Uvicorn for the local API, plain HTML, CSS, and JavaScript, no build step, no Node
- TradingView Lightweight Charts, Apache 2.0, from CDN, line and area series only in v1
- Tests with the Python standard library, no extra test framework in v1

## Code standards, short version

- Python: plain, readable, typed where it helps, no clever one liners. One function does one job.
- Do not add a dependency without a reason written in DECISIONS.md and in the task note.
- Every scraper returns the same observation shape, and logs the source URL and the time it ran.
- Every derived job is rebuildable from observations. If a job cannot be rerun safely, it is wrong.
- Frontend: no framework, no build step. One chart component, used for both dollar charts and index charts. The only difference is the vertical axis label and the data source.
- Do not add accounts, tracking, ads, affiliate links, or analytics in v1.
- Final report, always: end every task with one final report inside a single code block, so Austin can copy it. Do not end with plain chat text only, and do not end with no report. The code block must include: task name and status, files changed, exact command output for tests, URLs checked with status 200 or 404, and what is next. Do not start the next task in the same report. Stop after the code block and wait for Austin.

## Scraping rules, short version

- Respect robots.txt. If product pages are off limits, stop and report it, do not work around it.
- Read the terms of service for automated access, scraping, and robots. Note any ban. This is a research check, not legal advice.
- New products only. Only listings sold by the retailer itself, or fulfilled by it. Third party marketplace sellers are skipped in v1.
- Polite requests only: one product page at a time, a short delay between requests, a clear user agent that names this project, and a modest daily volume from the hand picked list.
- If a retailer blocks a simple fetch, or shows a CAPTCHA, stop that retailer, record the result in RETAILER_FEASIBILITY.md, and keep v1 working without it. Amazon is expected to be hard.

## Data rules, short version

- Observations are the source of truth, append only, never overwritten.
- sku_prices and index_values are derived, stored, and kept. They grow each period, they are not wiped as a routine step.
- Rebuild only when the method changes, when a scraping or matching bug produced bad prices, or when the period length changes. If a rebuild changes published numbers, the site must say so. See METHODOLOGY.md.
- A new SKU is left out of the index until it has its own history. It counts from its second period, through its own change only.

## Run commands, Windows

Run from the repo root, with the virtual environment active.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts\init_db.py
python scripts\scrape_once.py
python scripts\build_derived.py
python scripts\serve.py
python -m unittest discover -s tests -v
```

If a script in that list does not exist yet, its task in TASKS.md is not done. Do not invent a different command.

## Files to read first, by task

- Any task: TASKS.md, then the task section, then `.clinerules/00-read-first.md`
- Plan or scope: PROJECT_PLAN.md, DECISIONS.md
- Index math: METHODOLOGY.md, `tests/test_index.py`
- Layout and API: ARCHITECTURE.md
- Retailer work: RETAILER_FEASIBILITY.md, `config/retailers.yaml`, `.clinerules/02-scraping-rules.md`
- Data work: `.clinerules/03-data-and-index-rules.md`, `db/schema.sql`
- Frontend work: `.clinerules/04-frontend-rules.md`, `web/`
