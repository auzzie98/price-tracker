# Decisions

Add a row when something new is decided, and change one if we reverse it. Date, decision, and reason. Do not change scope in a code file alone.

| Area | Decision | Date |
| --- | --- | --- |
| Product | Open source, no account price research tool for GPUs, CPUs, and RAM | 2026-11-22 |
| Product | Long term goal is a credible inflation reference | 2026-11-22 |
| Chart | Stock style chart of price over time, refresh interval set during prototyping | 2026-11-22 |
| Data | Scraped, sources shown publicly, no affiliates, no budget | 2026-11-22 |
| Data | Store all raw observations, derive everything else | 2026-11-22 |
| Data | Cold start shown honestly, no backfill in v1 | 2026-11-22 |
| Method | Track at SKU level, chain an equal weighted matched model index starting at 100 | 2026-11-22 |
| Method | Per SKU price is the median across in stock retailers per period | 2026-11-22 |
| Pages | SKU page shows dollar price, like a ticker, category page shows the index, like an index fund | 2026-11-22 |
| Matching | Prototype product matching per retailer, basic and working beats perfect | 2026-11-22 |
| License | Permissive, MIT or Apache, final pick pending | 2026-11-22 |
| Hosting | Azure for Students, terms to verify | 2026-11-22 |
| Tools | VS Code with Cline and a free Nvidia model | 2026-11-22 |
| Deferred | Use mock data to finish Tasks 10 to 14, real live data source deferred, by Austin decision 2026-11-22 | 2026-11-22 |
| Pricing | New products only | 2026-11-22 |
| Sellers | Retailer sold or retailer fulfilled listings only, third party marketplace sellers skipped in v1 | 2026-11-22 |
| Products | Hand picked starting list, tracked by manufacturer part number | 2026-11-22 |
| Matching | Part number is the working rule, confirmed or changed while prototyping | 2026-11-22 |
| Out-of-stock | If a SKU has no in-stock observation for 7 days, it leaves the basket until it has an in-stock price again, then re-enters from its second period, following the matched model rule | 2026-11-22 |
| Site | Stock site layout: index tiles and top lists on the front page, category pages, product pages | 2026-11-22 |
| Front page | Biggest movers first, 1D and 1W, cheapest and most viewed lists in later releases | 2026-11-22 |
| Index storage | index_values is kept and grows each period, rebuilt from raw data only if the method changes, and the site says so if published numbers change | 2026-11-22 |
| Agents | Cline with Nemotron 3.5 Super VL first, fall back to Nemotron 3 Super, use Ultra for hard tasks, Devstral as backup | 2026-11-22 |
| Retailers | Test Amazon, Newegg, Micro Center, Best Buy, and B and H, Amazon dropped for v1 if it blocks us | 2026-11-22 |
| Stack | Python 3.12, SQLite, Requests and BeautifulSoup, FastAPI and Uvicorn, plain HTML, CSS, and JavaScript, no build step, no Node, TradingView Lightweight Charts, Apache 2.0, from CDN | 2026-11-22 |
| Stack | Prototype runs locally on Windows only, no deployment until Azure for Students is verified | 2026-11-22 |
| Refresh | Provisional default 6 hours in config/settings.yaml, shortest practical interval to be found during prototyping | 2026-11-22 |
| Refresh | 6 hours chosen because retailers are blocked for live scraping, mock data is used for prototype, and 6 hours equates to 4 checks per day per page, keeping volume modest | 2026-11-22 |
| Model | Nemotron 3.5 Super VL, 120B total, 12B active, context up to 1M tokens in the weights, hosted page lists 262K, plan work for 262K | 2026-11-22 |
| Scraper test | Headless browser test only for Best Buy first, after plain Requests fetch was blocked with HTTP 403 Cloudflare for all 5 retailers; no full scraper built yet | 2026-11-22 |
