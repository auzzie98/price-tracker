# TASKS.md

This is the starter task list for the coding agent. It was the last file Claude was working on before it ran out of free messages, and it is now complete in this repo.

## How to use this file

Austin is the boss. Cline is the coder. Austin decides scope, picks products and retailers, and approves each phase. Cline does the coding, one task at a time, in order.

Rules for the coder:
- Do one task at a time, in order. Do not skip ahead. Do not start a task until the previous task check is green.
- Read `.clinerules/00-read-first.md` before any code change.
- Small steps only. One file or one small change per edit, then run the check for that task.
- Check off a task only when its Done check is green, with the exact command output to prove it. A task is not done because the code looks right.
- If a check fails, fix it before moving on. Do not mark the task done and do not start the next task.
- If a task needs a decision from Austin, stop that task, write down the exact question, and wait. Do not guess a scope decision.
- Never invent a price, a retailer result, a license, or a hosting fact. Mark it as to check.

Rules for Austin:
- Open VS Code in this repo folder, open Cline, and paste one task at a time, or type the workflow name for that task. See Workflows below.
- Review the Done check output before saying yes to the next task.
- The product and retailer picks are yours. Tasks 5, 6, and 11 need your exact product page URLs and your manufacturer part numbers.

## Workflows, the commands for the bot

Cline Workflows are slash commands. The files live in `.clinerules/workflows/`. In Cline, type a slash and the file name, with no extension.

- `/start-prototype` : Task 1, create the skeleton and install dependencies
- `/check-retailer` : Task 5, test one retailer for robots.txt, terms, simple fetch, and price location
- `/add-retailer` : Task 6 and Task 11, add one retailer scraper after its check passes
- `/add-product` : Task 7 and Task 11, add one hand picked product at a time
- `/rebuild-index` : Task 13, rebuild sku_prices and index_values only when METHODOLOGY.md allows it
- `/run-checks` : any task, run all checks before marking a task done

If a workflow file is missing, use the task text below instead. The task text is the source of truth, the workflow is a shortcut.

## Context tips for the free model

Model: Nemotron 3.5 Super VL first, `nvidia/nemotron-3.5-super-vl-120b-a12b`, 120B total, 12B active, vision language, context up to 1M tokens in the weights. The hosted page lists 262K context, so plan work for 262K and treat 1M as the weights limit, not the hosted limit.
Fallback: Nemotron 3 Super, text only, 1M context in the weights.
Hard tasks only: Nemotron 3 Ultra, slower, save for schema design, matching logic, or a costly mistake.
Backup for pure coding: Devstral 2, 256K context.
Limits: about 40 requests per minute, about 1,000 free credits to start, no card needed. Free tier is for prototyping and study, not production.
- Keep each task small, one file or one small change per edit. Read a file before changing it, do not guess its contents.
- If Cline describes a command in prose instead of running it, switch models rather than fighting it.
- If you hit a 429 rate limit, stop, wait, and tell Austin. Do not retry in a loop.
- Keep API keys and private data out of prompts, files, and scraped output.

## Run commands, Windows

Run from the repo root, with the virtual environment active. Use `python`, not `python3`.

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

If a script in that list does not exist yet, its task is not done. Do not invent a different command.

## Phase 1, skeleton and data

### Task 1, repo skeleton and install

Goal: a clean repo that installs on Windows, with no fake implementation.
Workflow: `/start-prototype`
Files: `requirements.txt`, `src/price_tracker/`, `scripts/`, `tests/`, `web/`, `config/`, `db/`, `data/`
Do:
- Check the folder structure in ARCHITECTURE.md. Create any missing folder.
- Pin versions in `requirements.txt` at install time, for requests, beautifulsoup4, pyyaml, fastapi, and uvicorn. Update the file in this task.
- Create the virtual environment, install, and run the tests. The tests in this repo are placeholders until Task 4, they must still run without an error.
Run:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```
Done check: install finishes with no error, tests run, and no script claims to work before its task is done.

### Task 2, database

Goal: a SQLite database created from schema, safe to run twice.
Workflow: none, use the task text.
Files: `db/schema.sql`, `scripts/init_db.py`, `src/price_tracker/db.py`, `src/price_tracker/config.py`
Do:
- Implement `scripts/init_db.py` to read `db/schema.sql` and create `data/price-tracker.db`.
- Implement config loading from `config/settings.yaml`, with database path, host, and port.
- Load retailers and products from config in code, do not hard code them.
Run:
```
python scripts\init_db.py
python scripts\init_db.py
python -m unittest discover -s tests -v
```
Done check: the database file exists, running init twice does not delete data and does not error, and the tables match `db/schema.sql`.

### Task 3, config for the prototype

Goal: real config for 3 starter products, not 50 at once.
Workflow: `/add-product`
Files: `config/settings.yaml`, `config/retailers.yaml`, `config/products.yaml`
Do:
- Confirm the refresh interval in `config/settings.yaml`. Provisional default is 6 hours. Record any change in DECISIONS.md.
- Fill in the first product in `config/products.yaml`: ASUS Dual RTX 5070 12GB, MPN DUAL-RTX5070-12G, with its exact page URL at Newegg. Austin provides the URL.
- Add 2 more starter products, one per category if possible, with MPN and exact URLs. Leave a URL as TO ADD if that retailer does not list it, do not guess a URL.
- Keep the full hand picked list for Task 11. Do not add it now.
Run:
```
python scripts\init_db.py
python -m unittest discover -s tests -v
```
Done check: 3 products are in config, each with a MPN, and at least one exact retailer URL per product. No guessed URLs.

### Task 4, median and index, with the worked example test

Goal: the index math works, proven by the worked example.
Workflow: none, use the task text.
Files: `src/price_tracker/index.py`, `scripts/build_derived.py`, `tests/test_index.py`, `tests/test_median.py`
Do:
- Implement median price per SKU per period, from in stock observations only. Out of stock listings are ignored. If a SKU has no in stock price in a period, it has no sku_prices row.
- Implement the chained, equal weighted, matched model index from METHODOLOGY.md, starting at 100, skipping a new SKU until its second period.
- Implement `scripts/build_derived.py` to build sku_prices, then index_values, in order. Rerunning with no new observations must not duplicate rows.
- Replace the placeholder tests with real tests for the median cases and for the worked example.
Run:
```
python -m unittest discover -s tests -v
python scripts\build_derived.py
python scripts\build_derived.py
```
Done check: `tests/test_index.py` passes with Days 1 to 4, indexes 100.00, 99.00, 97.35, and 95.65. `tests/test_median.py` passes, including an out of stock listing ignored and a single retailer case. Rerunning build_derived does not duplicate rows.

## Phase 2, one retailer end to end

Do not start Phase 2 until Phase 1 checks are green.

### Task 5, retailer feasibility, one retailer

Goal: know whether one retailer can be scraped, with evidence.
Workflow: `/check-retailer`
Files: `RETAILER_FEASIBILITY.md`, `config/retailers.yaml`
Do:
- Pick one retailer first. Recommended first: Newegg. Amazon is expected to be hardest, test it, but do not let it block the prototype.
- For that retailer, run the 5 checks in RETAILER_FEASIBILITY.md: robots.txt, terms of service, simple fetch test, where the price lives, and request volume.
- Fill in that retailer row, with the date and the exact page checked. Use plain words: allowed, blocked, unclear, or to check.
- If it fails, set enabled to false in `config/retailers.yaml`, with a note and a date, and keep v1 working without it.
Run: no code run in this task, except opening the pages. Record what you saw.
Done check: one retailer row is filled in, with evidence, and the enabled flag matches the verdict.

### Task 6, one scraper, one product, one observation

Goal: one real observation in the database, from one retailer.
Workflow: `/add-retailer`
Files: `src/price_tracker/scrape/base.py`, `src/price_tracker/scrape/newegg.py`, `scripts/scrape_once.py`
Do:
- Implement shared scraper behavior in `base.py`: one page at a time, delay from settings, clear user agent, polite errors, no retry storm.
- Implement the retailer module for the retailer from Task 5. Same input and same output shape as base. Price parsing lives in the retailer module only.
- Implement `scripts/scrape_once.py` to scrape one product once, and write one observation, with timestamp, SKU, retailer, price in cents, in stock flag, and source URL.
- If the price is not found, log it as not found and write no observation. Do not guess a price and do not write a zero.
Run:
```
python scripts\scrape_once.py --retailer newegg
python scripts\build_derived.py
python -m unittest discover -s tests -v
```
Replace newegg with the retailer id from Task 5.
Done check: one observation is in the database, with the right SKU, retailer, price, in stock flag, and source URL. One sku_prices row follows from it.

### Task 7, one product page chart, with real data

Goal: one product page that draws a real dollar chart, even with only a few points.
Workflow: none, use the task text.
Files: `web/product.html`, `web/static/js/chart.js`, `web/static/js/api.js`, `scripts/serve.py`
Do:
- Implement the read only API for one product: `GET /api/products/{sku}`, returning sku_prices rows with period and median price.
- Implement the chart component in `chart.js` with TradingView Lightweight Charts, line series, time scale, and 1D, 1W, 1M, 1Y toggles filtering the same series.
- Build `web/product.html` to show the dollar price chart for the product from Task 6, plus which retailers its price comes from.
- Implement `scripts/serve.py` to serve the API and the static site locally.
Run:
```
python scripts\serve.py
```
Then open `http://127.0.0.1:8000` in a browser, and open the product page.
Done check: the product page loads, the chart draws from the API, not from hard coded data, and the retailer source is shown. With only a few points, the chart is short, and the page says history is building up.

## Phase 3, site and lists

### Task 8, front page and API

Goal: the front page shows index tiles and biggest movers, from real data.
Workflow: none, use the task text.
Files: `web/index.html`, `web/static/css/style.css`, `scripts/serve.py`
Do:
- Implement `GET /api/indexes`, `GET /api/indexes/{category}`, `GET /api/products`, and `GET /api/movers?range=1d`.
- Build `web/index.html` with index tiles for All GPUs, All CPUs, and All RAM, each with current value, percent change, and a small chart.
- Below the tiles, add the biggest movers list, with a 1D and 1W toggle. Leave room in the layout for the cheapest and most viewed lists later.
- Style strict black and white, plain and readable.
Run:
```
python scripts\serve.py
python -m unittest discover -s tests -v
```
Done check: the front page loads, tiles and movers come from the API, and on launch day the movers list says openly that it needs at least two data points per product.

### Task 9, category page

Goal: one category page that draws the index chart.
Workflow: none, use the task text.
Files: `web/category.html`, `web/static/js/chart.js`
Do:
- Use the same chart component as Task 7. The only difference is the vertical axis label and the data source: index_values, not dollars.
- Build `web/category.html` with the full index chart for one category, plus the list of tracked products in it.
- Link each product in the list to its product page.
Run:
```
python scripts\serve.py
```
Done check: the category page loads, the index chart draws from `/api/indexes/{category}`, and the product list matches `config/products.yaml`.

### Task 10, methodology page

Goal: the site explains itself, honestly.
Workflow: none, use the task text.
Files: `web/methodology.html`
Do:
- Copy the method from METHODOLOGY.md, in plain words: median per SKU, chained equal weighted index starting at 100, worked example, and the v1 limits.
- List which sites are scraped, with sources shown, and the cold start: charts begin at launch and history accumulates, no backfill in v1.
- Add the revision rule: if a rebuild changes published numbers, the site says so.
Run:
```
python scripts\serve.py
```
Done check: the methodology page loads, matches METHODOLOGY.md, and every index page links to it.

## Phase 4, expand and harden

### Task 11, remaining retailers and the hand picked list

Goal: expand from one retailer and 3 products to the full v1 test set, one at a time.
Workflow: `/check-retailer`, then `/add-retailer`, then `/add-product`, one at a time.
Files: `src/price_tracker/scrape/`, `config/retailers.yaml`, `config/products.yaml`, `RETAILER_FEASIBILITY.md`
Do:
- For each remaining retailer, Amazon, Micro Center, Best Buy, and B and H, run Task 5 first, then add the scraper only if the check passes.
- Expand the hand picked list, one product at a time, with MPN and exact URLs. Recommended start: 50 GPUs, 20 CPUs, 20 RAM kits, or the list Austin provides. Do not add them in one batch.
- Record the request volume for the full list at the interval in settings. With 6 hours, that is 4 scrapes per day per page.
Run, for each retailer and product:
```
python scripts\scrape_once.py --retailer bestbuy
python scripts\build_derived.py
python -m unittest discover -s tests -v
```
Done check: each retailer has a feasibility row and a scraper only if it passed, each product has a MPN and exact URLs, and a full scrape run writes observations with no duplicates on rerun.

### Task 12, refresh interval and out of stock rule

Goal: decide the two rules that were deferred to prototyping, with evidence.
Workflow: none, use the task text.
Files: `config/settings.yaml`, `METHODOLOGY.md`, `DECISIONS.md`
Do:
- Test the shortest practical refresh interval. Start at 6 hours, try shorter only if the retailers allow it and the volume stays modest. Record the interval chosen and why.
- Decide the out of stock rule: how long a SKU can go without a price before it leaves the basket. Record the rule in METHODOLOGY.md and DECISIONS.md.
- Update `config/settings.yaml` with the chosen interval.
Run:
```
python scripts\scrape_once.py
python scripts\build_derived.py
python -m unittest discover -s tests -v
```
Done check: the interval and the out of stock rule are written down, with dates, and the code follows them. No silent default remains.

### Task 13, rebuild and revision test

Goal: prove a rebuild works, and that a changed number is noted.
Workflow: `/rebuild-index`
Files: `scripts/build_derived.py`, `web/methodology.html`, `DECISIONS.md`
Do:
- Back up the database file before the rebuild, and record the backup name.
- Rebuild in order: observations, then sku_prices, then index_values, with `python scripts\build_derived.py --rebuild`.
- Run the index test and check the worked example still passes.
- Compare old and new index_values. If any published number changed, update the methodology page to say so, with dates and reason.
Run:
```
python scripts\build_derived.py --rebuild
python -m unittest discover -s tests -v
```
Done check: no duplicate rows, the worked example test passes, and any changed published number is noted on the methodology page.

## Phase 5, package

### Task 14, consistency check and clean clone test

Goal: the repo is ready for Austin to hand to a teammate, or to publish.
Workflow: `/run-checks`
Files: all, especially README.md, PROJECT_PLAN.md, and TASKS.md
Do:
- Run all checks in `.clinerules/workflows/run-checks.md`.
- Check that README.md quick start matches the real commands, that PROJECT_PLAN.md matches the code, and that TASKS.md matches what was actually done. Fix any drift, do not leave it.
- Check that no file contains an API key, a password, or a private file, and that `.gitignore` covers `data/`.
- Do a clean clone test: copy the repo to a new folder, without `venv/` and without `data/`, install, init the database, run tests, and serve. Record the result.
- Do not add a license file or deploy anything in this task. License and hosting are still open, see DECISIONS.md.
Run:
```
python -m unittest discover -s tests -v
python scripts\init_db.py
python scripts\build_derived.py
python scripts\serve.py
```
Done check: all checks pass, the clean clone test passes, and README.md, PROJECT_PLAN.md, and TASKS.md agree with the code.

## Open questions, deferred on purpose

These are not tasks yet. Do not start them in v1 unless Austin says so.

- License: MIT or Apache 2.0, pros and cons during prototyping, then choose, and decide whether the data is open too.
- Azure for Students: confirm credit amount, expiry, and what the plan covers, once it is needed.
- Tech stack and repo location: stack is chosen in PROJECT_PLAN.md for the prototype. Repo location, GitHub, is decided when the code is ready to publish.
- Monetization: ads and premium alerts, later release only. No code for them in v1.
- Cheapest and most viewed front page lists: later releases, after biggest movers works.
- Refresh interval, out of stock rule, and SKU matching: decided in Task 12, and in prototyping for matching, not before.

## Status

Pre draft planning is done. This file completes the starter repo. Prototyping starts at Task 1.
