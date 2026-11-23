# 02 Scraping rules

## Respect the site

- Open and read `/robots.txt` first. If product pages are off limits to bots, stop and report it. Do not work around it.
- Read the terms of service for automated access, scraping, and robots. Note any ban. This is a research check, not legal advice.
- If a retailer blocks a simple fetch, or shows a CAPTCHA, stop that retailer, record the result in RETAILER_FEASIBILITY.md, and keep v1 working without it.

## What counts as a price

- New products only.
- Only listings sold by the retailer itself, or fulfilled by it. Third party marketplace sellers are skipped in v1.
- One observation is one scraped data point: timestamp, SKU, retailer, price, in stock flag, plus source URL.
- Price is stored in cents, as an integer, in the database. Display it in dollars on the site.

## How to scrape

- One module per retailer in `src/price_tracker/scrape/`, sharing `base.py`.
- Same input for every scraper: a SKU and a product page URL from `config/products.yaml`.
- Same output for every scraper: an observation, with source URL and run time logged.
- One page at a time, a short delay between requests, from `config/settings.yaml`, a clear user agent that names this project, and a modest daily volume from the hand picked list.
- Price parsing lives in the retailer module only, since each site puts the price in a different place.
- If the price is not found, log it as not found, with the URL and time. Do not guess a price, do not reuse an old price, and do not write a zero price as if it were real.
- No headless browser in v1. No proxy, no paid feed, no workaround without a new decision in DECISIONS.md.
