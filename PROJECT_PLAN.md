# Price Tracker: Final Project Plan

Date: 2026-11-22
Status: Pre draft planning done. Prototyping starts at Task 1 in TASKS.md.
Source of truth: this plan, plus METHODOLOGY.md, ARCHITECTURE.md, DECISIONS.md, and TASKS.md. If they disagree, this plan wins for scope, and METHODOLOGY.md wins for the index math.

## 1. Vision

An open source website that tracks computer part prices over time and draws them like a stock chart, so anyone who can read a chart can see at a glance whether prices are rising or falling.

Who it is for: researchers and price watchers, with GPU buyers as the core audience and RAM and CPU buyers as the second wave.
Why people use it: a simple, clear chart of price over time, and a legitimate backend and codebase that does what the site says it does.
Long term: a credible public reference for hardware price inflation that a team or company could take over and turn into something economists cite.
Money, later release only: ads and premium alerts. Not part of v1.

## 2. Scope of v1

v1 is a proof of concept. A basic working version beats a perfect economic model.

In v1:
- GPUs, CPUs, RAM
- Public, no accounts, fully open source
- Scraped prices with sources shown on the site
- SKU price charts and category index charts
- Honest cold start, history builds up from launch
- Free to use

Not in v1, for later releases:
- Other components. A full list is compiled before a full release.
- User accounts, saved lists
- Affiliate links, paid data feeds
- Quality adjustment, weighting, economist grade methodology
- Backfilled history from open datasets
- Ads and premium price alerts

## 3. Site structure

The site is laid out like a stock site: indexes and top lists on the front page, and a page for every tracked product. All charts are the same line chart with 1D, 1W, 1M, and 1Y toggles.

Front page: index tiles for All GPUs, All CPUs, and All RAM, each with current value, percent change, and a small chart. Below them, the top lists.
Category page: the full index chart for one category, plus the list of tracked products in it.
Product page: the dollar price chart for one exact product, plus which retailers its price comes from.
Methodology page: how the index works, which sites are scraped, the v1 limits, and the cold start.

Front page lists, all drawn from sku_prices:
- Biggest movers: largest price drops and rises over 1 day or 1 week. In the prototype.
- Cheapest and biggest discount: lowest current price, or largest drop from a recent high. Later.
- Most viewed: products with the most page views, using an anonymous counter. Later.

On launch day the lists are empty, since movers need at least two data points per product. The site says so openly.

## 4. Vocabulary

A SKU is one exact product, not a chip. The same SKU is shared across retailers selling that identical product, matched by manufacturer part number (MPN). Every agent uses these terms the same way.

- Architecture: chip generation, an optional grouping. Example: Blackwell, Ada, Turing.
- Chip: the GPU or CPU silicon, used for family pages. Example: RTX 5070.
- SKU: one exact product from one manufacturer, the unit we track. Example: ASUS Dual RTX 5070 12GB, part number DUAL-RTX5070-12G.
- Retailer: a store listing a SKU. Example: Newegg, Micro Center, Best Buy.
- Observation: one scraped data point: timestamp, SKU, retailer, price, in stock flag. Example: Day 1 09:00, ASUS Dual 5070, Newegg, 505 dollars, in stock.
- Index: a number that tracks percent price change across a basket of SKUs, starting at 100. Example: GPU Index 95.65.

What makes two listings the same SKU or different SKUs:
- Same SKU: the identical product listed at Newegg, Micro Center, and Best Buy.
- Different SKUs: an ASUS card and an MSI card with the same chip, the OC and non OC versions from one maker, different VRAM sizes, boxed versus tray or OEM CPUs.
- RAM: a SKU is a specific kit, brand, capacity, speed, latency, such as 32GB DDR5-6000 CL30. Matching these is expected to be messy.

## 5. Method, short version

v1 uses a chained, equal weighted, matched model index. A SKU price is the median across in stock retailers per period. The index averages each SKU own percent change, never dollar prices across different products.

Full math, worked example, and limits are in METHODOLOGY.md. Do not rederive the method in code comments. Link to that file.

## 6. Data and architecture, short version

Prices are scraped from retailers, with every source shown publicly on the site. Raw scrapes are the permanent record and everything else is recomputed from them.

1. Scrapers collect listings from each retailer and write them to observations, append only, never overwritten.
2. A job turns observations into sku_prices: the median price per SKU per period, from in stock listings.
3. A second job turns sku_prices into index_values: one row per category per period, with the number of SKUs used.
4. The website draws SKU pages from sku_prices, dollar price, like a ticker, and category pages from index_values, index, like the S and P 500.

Full layout, file map, and API shape are in ARCHITECTURE.md.

## 7. Retailers and listing rules

Test first: Amazon, Newegg, Micro Center, Best Buy, and B and H. Amazon blocks scrapers aggressively, so v1 must still work if it has to be dropped. Sources are shown publicly, so a missing retailer breaks nothing.

Listing rules for v1:
- New products only.
- Only listings sold by the retailer itself or fulfilled by it. Third party marketplace sellers are skipped.
- A hand picked starting list, recording each product manufacturer part number and its page URL at each retailer.

Feasibility checks, one per retailer, are in RETAILER_FEASIBILITY.md: robots.txt, terms of service, simple fetch test, where the price lives, and request volume.

## 8. Tech stack, chosen for the prototype

- Python 3.12 on Windows, virtual environment, `python` not `python3`, activate with `venv\Scripts\activate`
- SQLite, `db/schema.sql` as the source of truth, database file in `data/`, never committed
- Requests and BeautifulSoup for scrapers, one module per retailer, no headless browser in v1
- FastAPI and Uvicorn for the local API, plain HTML, CSS, and JavaScript for the site, no build step and no Node
- TradingView Lightweight Charts, Apache 2.0, loaded from CDN, line and area series, time scale, 1D, 1W, 1M, 1Y toggles
- Cline in VS Code, Nemotron 3.5 Super VL first, see AGENTS.md

Why this stack: it is small enough for a free model to build in small tasks, it has no paid services in v1, it runs locally on Windows, and every part can be inspected in plain files. If a part proves wrong in prototyping, change it in DECISIONS.md and update this plan, do not silently drift.

## 9. Agent setup

Cline in VS Code, provider NVIDIA Build, free endpoint.
- Default: nemotron-3.5-super-vl-120b-a12b. Vision language model, 120B total, 12B active, context up to 1M tokens in the weights. The hosted page lists 262K context, so plan work for 262K and treat 1M as the weights limit, not the hosted limit. About 40 requests per minute, about 1,000 free credits to start, no card needed. Free tier is for prototyping and study, not production.
- Fallback: nemotron-3-super-120b-a12b, same family, text only, 1M context in the weights.
- Hard tasks only: nemotron-3-ultra-550b-a55b, slower, save for schema design, matching logic, or a costly mistake.
- Backup for pure coding: devstral-2-123b-instruct-2512, 256K context.
- If Cline describes a command in prose instead of running it, switch models rather than fighting it.
- Keep API keys and private data out of prompts. Free providers may log prompts.

Cline reads AGENTS.md and `.clinerules/` automatically. Workflows, the slash commands for the bot, live in `.clinerules/workflows/` and are listed in TASKS.md.

## 10. Work plan

Work is in TASKS.md, one task at a time, in order. Each task has a goal, a done check, and the exact run command to prove it.

Phase 1, skeleton and data: Task 1 to Task 4. Repo skeleton, database, config, and the index test from the worked example.
Phase 2, one retailer end to end: Task 5 to Task 7. Retailer feasibility for one retailer, one scraper, one product, one chart.
Phase 3, site and lists: Task 8 to Task 10. Front page, category page, product page, biggest movers.
Phase 4, expand and harden: Task 11 to Task 13. Remaining retailers, hand picked list, rebuild and revision rules.
Phase 5, package: Task 14. Consistency check, README check, and a clean clone test.

Do not start Phase 2 until Phase 1 checks are green. Do not add a retailer until the first retailer works end to end.

## 11. Open questions, deferred on purpose

- Retailer feasibility: done in prototyping, between Austin and the coding agent, using RETAILER_FEASIBILITY.md.
- Azure for Students: confirm credit amount, expiry, and what the plan covers, once it is needed.
- License: MIT or Apache 2.0, pros and cons during prototyping, then choose, and decide whether the data is open too.
- Refresh interval: find the shortest practical interval during prototyping. Provisional default in `config/settings.yaml` is 6 hours.
- Product matching: confirm part number matching while prototyping on one retailer, then expand.
- Out of stock rule: decide how long a SKU can go without a price before it leaves the basket.
- Tech stack and repo location: stack is chosen above for the prototype. Repo location, GitHub, is decided when the code is ready to publish.
- Monetization: ads and premium alerts, later release only. No code for them in v1.

## 12. How to change this plan

Add a row to DECISIONS.md, with date and reason, then update the affected section here and in TASKS.md. Do not change scope in a code file alone.
